/*
*    Copyright (c) 2016 Broadcom Corporation
*    All Rights Reserved
* 
*  This program is the proprietary software of Broadcom Corporation and/or its
*  licensors, and may only be used, duplicated, modified or distributed pursuant
*  to the terms and conditions of a separate, written license agreement executed
*  between you and Broadcom (an "Authorized License").  Except as set forth in
*  an Authorized License, Broadcom grants no license (express or implied), right
*  to use, or waiver of any kind with respect to the Software, and Broadcom
*  expressly reserves all rights in and to the Software and all intellectual
*  property rights therein.  IF YOU HAVE NO AUTHORIZED LICENSE, THEN YOU HAVE
*  NO RIGHT TO USE THIS SOFTWARE IN ANY WAY, AND SHOULD IMMEDIATELY NOTIFY
*  BROADCOM AND DISCONTINUE ALL USE OF THE SOFTWARE.
* 
*  Except as expressly set forth in the Authorized License,
* 
*  1. This program, including its structure, sequence and organization,
*     constitutes the valuable trade secrets of Broadcom, and you shall use
*     all reasonable efforts to protect the confidentiality thereof, and to
*     use this information only in connection with your use of Broadcom
*     integrated circuit products.
* 
*  2. TO THE MAXIMUM EXTENT PERMITTED BY LAW, THE SOFTWARE IS PROVIDED "AS IS"
*     AND WITH ALL FAULTS AND BROADCOM MAKES NO PROMISES, REPRESENTATIONS OR
*     WARRANTIES, EITHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE, WITH
*     RESPECT TO THE SOFTWARE.  BROADCOM SPECIFICALLY DISCLAIMS ANY AND
*     ALL IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, NONINFRINGEMENT,
*     FITNESS FOR A PARTICULAR PURPOSE, LACK OF VIRUSES, ACCURACY OR
*     COMPLETENESS, QUIET ENJOYMENT, QUIET POSSESSION OR CORRESPONDENCE
*     TO DESCRIPTION. YOU ASSUME THE ENTIRE RISK ARISING OUT OF USE OR
*     PERFORMANCE OF THE SOFTWARE.
* 
*  3. TO THE MAXIMUM EXTENT PERMITTED BY LAW, IN NO EVENT SHALL BROADCOM OR
*     ITS LICENSORS BE LIABLE FOR (i) CONSEQUENTIAL, INCIDENTAL, SPECIAL,
*     INDIRECT, OR EXEMPLARY DAMAGES WHATSOEVER ARISING OUT OF OR IN ANY
*     WAY RELATING TO YOUR USE OF OR INABILITY TO USE THE SOFTWARE EVEN
*     IF BROADCOM HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES;
*     OR (ii) ANY AMOUNT IN EXCESS OF THE AMOUNT ACTUALLY PAID FOR THE
*     SOFTWARE ITSELF OR U.S. $1, WHICHEVER IS GREATER. THESE LIMITATIONS
*     SHALL APPLY NOTWITHSTANDING ANY FAILURE OF ESSENTIAL PURPOSE OF ANY
*     LIMITED REMEDY.
*/

/*
 * bcmTransport.c
 *
 */

#include "bcmApi.h"
#include "bcmEmmiParser.h"
#include "bcmTransportInternal.h"
#include "bcmUdpTransportDriver.h"
#include "bcmTraceLogDebug.h"

typedef enum { bcmChIdxConfig, bcmChIdxAuto } bcmChannelIdx;

static bcmTransport *transports[BCM_TR_MAX_OLTS][2]; /* Per OLT, per config/auto channel transports */

static F_bcmAutoHandler autoHandler;
static U32 autoFlags;

static int _bcmTrRxThreadHandler(void *arg);

/* Free reassemble block */
static void _bcmTrReassBlockFree(bcmTrReass **prb)
{
    bcmTrReass *reass = *prb;
    U32 i;

    for (i=0; i<reass->numFragments; i++)
    {
        if (reass->fragments[i].buf)
            bcmOsFree(reass->fragments[i].buf);
    }
    bcmOsFree(reass);
    *prb = NULL;
}

/* Notify application that message is ready */
static void _bcmTrHdrNotifyReady(bcmTransport *tr, bcmTrHdr *hdr)
{
    hdr->timestamp = bcmOsGetCurrentTimeMs();
    bcmOsSemPut(&hdr->sem);
}

/* Free transport header. Called under transport lock */
static void _bcmTrHdrFree(bcmTransport *tr, bcmTrHdr *hdr, bcmTrHdrList *curList)
{
    bcmMsg *msg = hdr->msg;

    /* Remove from the list it is in, if any */
    if (curList)
        TAILQ_REMOVE(curList, hdr, l);

    bcmBufFree(&hdr->txBuf);
    bcmBufFree(&hdr->rxBuf);
    if (hdr->reass)
        _bcmTrReassBlockFree(&hdr->reass);
    memset(hdr, 0, BCM_TR_HDR_CLEAR_SIZE);

    /* Request-response or autonomous ? */
    if (msg)
        TAILQ_INSERT_TAIL(&tr->freeReqList, hdr, l);
    else
        TAILQ_INSERT_TAIL(&tr->freeAutoList, hdr, l);
}

/* Pre-allocate transport header array, put all blocks on free lists */
static int _bcmTrHdrListAlloc(bcmTransport *tr)
{
    U32 nHdr, i;
    bcmTrHdr *hdr;

    nHdr = tr->cfg.maxRequests + tr->cfg.maxAutos;
    tr->trHdrArray = bcmOsCalloc(sizeof(bcmTrHdr) * nHdr);
    if (!tr->trHdrArray)
        return bcmErrNoMemory;

    hdr = tr->trHdrArray;
    for (i=0; i<tr->cfg.maxRequests; i++, hdr++)
    {
        TAILQ_INSERT_TAIL(&tr->freeReqList, hdr, l);
        bcmOsSemInit(&hdr->sem, 0);
    }
    for (i=0; i<tr->cfg.maxAutos; i++, hdr++)
    {
        TAILQ_INSERT_TAIL(&tr->freeAutoList, hdr, l);
    }
    return bcmErrOk;
}

/* Free transport headers */
static void _bcmTrHdrListFree(bcmTransport *tr)
{
    bcmTrHdr *hdr, *tmphdr;

    if (!tr->trHdrArray)
        return;

    TAILQ_FOREACH_SAFE(hdr, &tr->msgList, l, tmphdr)
    {
        bcmMsg *msg = hdr->msg;
        /* Release waiting task if request-response */
        if (msg && hdr->status == bcmErrInProgress)
        {
            msg->status = bcmErrCommFailure;
            msg->trHdr = NULL;
            bcmOsSemPut(&hdr->sem);
        }
        _bcmTrHdrFree(tr, hdr, &tr->msgList);
    }
    TAILQ_FOREACH_SAFE(hdr, &tr->freeReqList, l, tmphdr)
    {
        bcmOsSemDestroy(&hdr->sem);
    }
    bcmOsFree(tr->trHdrArray);
}

/* Pack EMMI header */
static inline void _bcmTrPackEmmiHdr(bcmTrHdr *trHdr, bcmBufInfo *buf)
{
    U16 len = bcmBufGetUsed(buf) - BCM_EMMI_HDR_SIZE;
    U16 *ptr = (U16 *)buf->start;
    *(ptr++) = bcmOsHost2BE_U16(trHdr->msgType);
    *(ptr++) = bcmOsHost2BE_U16(trHdr->corrTag);
    *(ptr++) = 0; /* sequence number */
    *(ptr++) = 0; /* status */
    *ptr = bcmOsHost2BE_U16(len);
}

/* Allocate transport header from the given free list.
 * Must be called under lock
 */
static inline bcmTrHdr *_bcmTrHdrGetFree(bcmTrHdrList *freeList)
{
    bcmTrHdr *trHdr = TAILQ_FIRST(freeList);
    if (trHdr)
        TAILQ_REMOVE(freeList, trHdr, l);
    return trHdr;
}

/* Unpack EMMI header */
static inline void _bcmTrUnpackEmmiHdr(U8 *buf, bcmEmmiHeader *emmiHdr)
{
    emmiHdr->type = bcmOsBE2Host_U16(*(U16 *)buf);
    emmiHdr->correlationTag = bcmOsBE2Host_U16(*(U16 *)&buf[2]);
    emmiHdr->fragmentNumber = bcmOsBE2Host_U16(*(U16 *)&buf[4]);
    emmiHdr->status = bcmOsBE2Host_U16(*(U16 *)&buf[6]);
    emmiHdr->length = bcmOsBE2Host_U16(*(U16 *)&buf[8]);
}

/* Is message autonomous ? */
static inline Bool _bcmTrMsgIsAuto(U16 cmd)
{
    return (cmd < 1000);
}

/* Find message by correlation tag and message type
 * Called under lock
 */
static bcmTrHdr *_bcmTrHdrGetByCorrTag(bcmTransport *tr, U16 cmd, U16 corrTag)
{
    bcmTrHdr *trHdr;

    TAILQ_FOREACH(trHdr, &tr->msgList, l)
    {
        if (trHdr->corrTag==corrTag && trHdr->msgType==cmd && trHdr->status == bcmErrInProgress)
            break;
    }
    return trHdr;
}

/* Message reassembler. Returns TRUE if message reassembling is completed */
static Bool _bcmTrReassemble(bcmTransport *tr, bcmTrHdr *trHdr, bcmEmmiHeader *emmiHdr, U8 *buf, U32 size)
{
    Bool isLast = (emmiHdr->status != (U16)bcmErrFragment);
    U16 fragmentNumber = emmiHdr->fragmentNumber;
    Bool done = FALSE;

    /* Single-buffer message ? */
    if (isLast && !fragmentNumber)
    {
        bcmBufInit(&trHdr->rxBuf, size, buf);
        trHdr->status = bcmErrOk;
        return TRUE;
    }

    /*
     * Multi-part message
     */

    /* Discard if invalid fragment number or duplicate */
    if (fragmentNumber >= tr->cfg.maxFragments ||
        (trHdr->reass && trHdr->reass->fragments[fragmentNumber].buf) )
    {
        bcmOsFree(buf);
        /* If last out-of range fragment was received report it.
         * We want to avoid request retransmission in this case */
        if (fragmentNumber >= tr->cfg.maxFragments)
        {
            trHdr->status = bcmErrTooManyFragments;
            return isLast;
        }
        ++tr->stat.fragInvalid;
        return FALSE;
    }

    /* Allocate reassembly buffer if not done yet and store fragment */
    if (!trHdr->reass)
    {
        trHdr->reass = bcmOsCalloc(sizeof(bcmTrReass) + tr->cfg.maxFragments * sizeof(bcmTrFragment));
        if (!trHdr->reass)
        {
            ++tr->stat.msgNoMem;
            bcmOsFree(buf);
            return FALSE;
        }
        trHdr->reass->fragments = (bcmTrFragment *)(trHdr->reass + 1);
    }
    trHdr->reass->fragments[fragmentNumber].buf = buf;
    trHdr->reass->fragments[fragmentNumber].bufSize = size;
    trHdr->reass->numFragments++;
    trHdr->reass->totalSize += size - BCM_EMMI_HDR_SIZE;
    if (isLast)
        trHdr->reass->maxFragment = fragmentNumber;
    done = (trHdr->reass->maxFragment && (trHdr->reass->numFragments > trHdr->reass->maxFragment));
    ++tr->stat.fragReceived;

    /* Reassemble if done */
    if (done)
    {
        /* Allocate big flat buffer */
        if (bcmBufAlloc(&trHdr->rxBuf, trHdr->reass->totalSize + BCM_EMMI_HDR_SIZE) == bcmErrOk)
        {
            U32 i;
            U8 *body = trHdr->rxBuf.start + BCM_EMMI_HDR_SIZE;

            for (i=0; i<trHdr->reass->numFragments; i++)
            {
                U32 fragSize = trHdr->reass->fragments[i].bufSize - BCM_EMMI_HDR_SIZE;
                bcmBugOn(!trHdr->reass->fragments[i].buf);
                memcpy(body, trHdr->reass->fragments[i].buf + BCM_EMMI_HDR_SIZE, fragSize);
                body += fragSize;
            }
            memcpy(trHdr->rxBuf.start, trHdr->reass->fragments[trHdr->reass->numFragments - 1].buf,
                BCM_EMMI_HDR_SIZE);
            trHdr->status = bcmErrOk;
        }
        else
        {
            /* Reassembly buffer allocation failed */
            trHdr->status = bcmErrNoMemory;
        }
    }
    else
    {
        /* More fragments expected. Update timestamp to prolong timing out */
        trHdr->timestamp = bcmOsGetCurrentTimeMs();
    }

    return done;
}

/* Unpack message. *unpacked is set=NULL in case of error */
static void _bcmTrMsgUnpack(bcmTransport *tr, bcmTrHdr *trHdr, void **unpacked)
{
    bcmMsg *msg = trHdr->msg;

    bcmBugOn(!trHdr->rxBuf.start);

    *unpacked = NULL;

    /* Unpack */
    if (!msg)
    {
        trHdr->status = bcmEmmiCmdIndex(trHdr->msgType, &trHdr->msgIdx);
        if (trHdr->status != bcmErrOk)
            return;
    }
    bcmBufSkip(&trHdr->rxBuf, BCM_EMMI_HDR_SIZE);
    trHdr->status = bcmEmmiMsgUnpack(trHdr->msgIdx, &trHdr->rxBuf, unpacked);
}

/* Handle rx data. Returns number of messages that was identified and reassembled. Can be 0 or 1 */
static int _bcmTrHandleRx(bcmTransport *tr, U8 *buf, U32 size)
{
    bcmEmmiHeader emmiHdr;
    bcmTrHdr *trHdr;
    int msgDone;
    bcmMsg *msg;
    void *unpacked;
    bcmErrno status;

    /* Transport lock */
    bcmOsMutexLock(&tr->mutex);

    /* If some data was received - handle it */
    if (size < BCM_EMMI_HDR_SIZE)
    {
        /* Message is too short */
        ++tr->stat.msgCommErr;
        goto rxDone;
    }

    _bcmTrUnpackEmmiHdr(buf, &emmiHdr);

    /* Find transport header. If not found - allocate new for autonomous message */
    trHdr = _bcmTrHdrGetByCorrTag(tr, emmiHdr.type, emmiHdr.correlationTag);
    if (!trHdr)
    {
        if (_bcmTrMsgIsAuto(emmiHdr.type))
        {
            /* Allocate new transport block */
            trHdr = _bcmTrHdrGetFree(&tr->freeAutoList);
            if (!trHdr)
            {
                ++tr->stat.msgTooManyAuto;
                goto rxDone;
            }
            trHdr->msgType = emmiHdr.type;
            trHdr->corrTag = emmiHdr.correlationTag;
            trHdr->status = bcmErrInProgress;
            TAILQ_INSERT_TAIL(&tr->msgList, trHdr, l);
        }
        else
        {
            /* No request - discard */
            ++tr->stat.msgNoReq;
            goto rxDone;
        }
    }
    msg = trHdr->msg;

    /* Reassemble. "buf" should not be used following this call */
    msgDone = _bcmTrReassemble(tr, trHdr, &emmiHdr, buf, size);

    /* If expects more parts - nothing more to do here */
    if (!msgDone)
        goto rxDone;

    /* Done reassembling. Unpack and deliver */
    /* Unpack only if there were no local or remote errors */
    if (!trHdr->status && !emmiHdr.status)
        _bcmTrMsgUnpack(tr, trHdr, &unpacked);
    status = trHdr->status ? trHdr->status : emmiHdr.status;

    /* Trace/log */
    bcmTdlCheckNotifyMsg(tr->olt, trHdr->msgIdx,
        trHdr->msg ? bcmMsgEventReceiveResp : bcmMsgEventReceiveAuto,
        status, &trHdr->rxBuf, unpacked);

    /* If response - notify waiting application.
     * Still under lock
     */
    if (msg)
    {
        /* Response. Transport header will be released by requester */
        ++tr->stat.msgRespReceived;
    }
    else
    {
        /* Autonomous. Release transport header here */
        _bcmTrHdrFree(tr, trHdr, &tr->msgList);
    }

    /* Now unlock and notify application. Autonomous handler is only called if message is OK */
    bcmOsMutexUnlock(&tr->mutex);

    if (msg)
    {
        *msg->response = unpacked;
        msg->status = status;
        _bcmTrHdrNotifyReady(tr, trHdr);
    }
    else if (unpacked)
    {
        if (autoHandler)
            autoHandler(tr->olt, emmiHdr.type, (bcmEmmiAutoMsg *)unpacked);
        if (!(autoFlags & bcmAutoMsgFlag_Keep))
            bcmOsFree(unpacked);
        ++tr->stat.msgAutoReceived;
    }
    return 1;

    /* Error return */
rxDone:
    bcmOsMutexUnlock(&tr->mutex);
    return 0;
}

/* Check for time-outs. returns number of messages timed out */
static int _bcmTrCheckTimeout(bcmTransport *tr)
{
    bcmTrHdr *trHdr, *tmp;
    U32 now;
    int nmsg = 0;

    /* Transport lock */
    bcmOsMutexLock(&tr->mutex);

    now = bcmOsGetCurrentTimeMs();
    TAILQ_FOREACH_SAFE(trHdr, &tr->msgList, l, tmp)
    {
        bcmMsg *msg = trHdr->msg;

        if (now - trHdr->timestamp <= tr->cfg.msgTimeout)
            continue;

        /* Retransmit ? */
        if (msg && trHdr->txCount <= tr->cfg.maxRetries)
        {
            tr->driver.send(tr, trHdr->txBuf.start, bcmBufGetUsed(&trHdr->txBuf));
            ++trHdr->txCount;
            trHdr->timestamp = bcmOsGetCurrentTimeMs();
            bcmTdlCheckNotifyMsg(tr->olt, trHdr->msgIdx, bcmMsgEventReTransmit,
                bcmErrOk, &trHdr->txBuf, trHdr->msg->request);
            continue;
        }

        /* Giving up */
        /* Release waiting task if request-response - unless it has already been done */
        if (msg)
        {
            if (trHdr->status == bcmErrInProgress)
            {
                trHdr->status = msg->status = bcmErrTimeout;
                _bcmTrHdrNotifyReady(tr, trHdr);
                ++tr->stat.msgNoResp;
            }
            else
            {
                /* We've already notified application. If message is stuck here - assume that
                 * application has died and release transport header
                 */
                if (now - trHdr->timestamp <= tr->cfg.msgReadyTimeout)
                    continue;
                msg->trHdr = NULL;
                _bcmTrHdrFree(tr, trHdr, &tr->msgList);
                ++tr->stat.msgReadyTimeout;
            }
        }
        else
        {
            _bcmTrHdrFree(tr, trHdr, &tr->msgList);
            ++tr->stat.msgReassTimeout;
        }
        ++nmsg;
    }
    tr->lastTimeOutCheck = bcmOsGetCurrentTimeMs();

    /* Release transport lock */
    bcmOsMutexUnlock(&tr->mutex);

    return nmsg;
}

/* Check for receive and timeouts */
static int _bcmTrPoll(bcmTransport *tr)
{
    U8 *buf = NULL;
    int nmsg = 0, nmsg_prev;

    do
    {
        bcmErrno rc;
        U32 bytesRcvd;

        nmsg_prev = nmsg;

        /* Receive */
        if (!buf)
        {
            buf = bcmOsMalloc(tr->cfg.maxMtuSize);
            if (!buf)
            {
                ++tr->stat.msgNoMem;
                break;
            }
        }

        rc = tr->driver.recv(tr, buf, tr->cfg.maxMtuSize, &bytesRcvd);
        if (rc == bcmErrOk)
        {
            nmsg += _bcmTrHandleRx(tr, buf, bytesRcvd);
            buf = NULL; /* now owned by rx handler above */
        }


        /* Check for timeouts if any */
        if (bcmOsGetCurrentTimeMs() - tr->lastTimeOutCheck > tr->periodTimeOutCheck)
        {
            /* Check requests waiting for acknowledge and multy-part messages for timeout.
             * Timed-out requests are retransmitted.
             */
            nmsg += _bcmTrCheckTimeout(tr);
        }
    } while(nmsg_prev != nmsg);

    if (buf)
        bcmOsFree(buf);

    return nmsg;
}


/* Rx thread handler */
static int _bcmTrRxThreadHandler(void *arg)
{
    bcmTransport *tr = (bcmTransport *)arg;

    while(!tr->kill_request)
    {
        _bcmTrPoll(tr);
        bcmOsSleep(1);
    }
    tr->kill_done = 1;

    return 0;
}

/*
 * External message interface
 */

/** Send message request */
bcmErrno bcmMsgSend(bcmOltIdx olt, bcmMsg *msg)
{
    bcmTransport *tr;
    bcmTrHdr *trHdr;
    bcmErrno rc;

    if (olt >= BCM_TR_MAX_OLTS)
        return bcmErrParm;

    tr = transports[olt][bcmTrChannelConfig];
    if (!tr || !tr->connected)
    {
        msg->status = bcmErrNotConnected;
        return bcmErrNotConnected;
    }

    bcmOsMutexLock(&tr->mutex);

    /* Allocate message transport header */
    trHdr = _bcmTrHdrGetFree(&tr->freeReqList);
    if (!trHdr)
    {
        ++tr->stat.msgNoReq;
        bcmOsMutexUnlock(&tr->mutex);
        return bcmErrTooManyRequests;
    }
    trHdr->msg = msg;

    /* Allocate transport buffer and pack */
    rc = bcmEmmiMsgPack(msg, &trHdr->txBuf);
    if (rc)
    {
        ++tr->stat.msgNoMem;
        goto cleanup;
    }

    trHdr->corrTag = ++tr->correlationTag;
    trHdr->msgType = msg->msgType;
    trHdr->msgIdx = msg->msgIdx;

    /* Pack correlation tag, command and length */
    _bcmTrPackEmmiHdr(trHdr, &trHdr->txBuf);

    /* Send using customer-provided driver */
    trHdr->status = bcmErrInProgress;
    rc = tr->driver.send(tr, trHdr->txBuf.start, bcmBufGetUsed(&trHdr->txBuf));
    if (rc != bcmErrOk)
    {
        ++tr->stat.msgCommErr;
        goto cleanup;
    }
    trHdr->timestamp = bcmOsGetCurrentTimeMs();
    msg->trHdr = trHdr;
    TAILQ_INSERT_TAIL(&tr->msgList, trHdr, l);
    ++tr->stat.msgSent;
    bcmTdlCheckNotifyMsg(tr->olt, trHdr->msgIdx, bcmMsgEventTransmit,
        bcmErrOk, &trHdr->txBuf, trHdr->msg->request);
    bcmOsMutexUnlock(&tr->mutex);

    return bcmErrOk;

    /* error */
cleanup:
    _bcmTrHdrFree(tr, trHdr, NULL);
    bcmOsMutexUnlock(&tr->mutex);
    return rc;
}

/** Wait and return response
 *
 * \param[in]   olt     OLT index
 * \param[in]   msg     message handle
 *                      It is caller's responsibility to release the message when no longer needed.
 * \return 0=success or error code
 */
bcmErrno bcmMsgWaitResponse(bcmOltIdx olt, bcmMsg *msg)
{
    bcmTransport *tr;

    if (olt >= BCM_TR_MAX_OLTS || !msg->response)
        return bcmErrParm;

    tr = transports[olt][bcmTrChannelConfig];
    if (!tr || !tr->connected)
    {
        msg->status = bcmErrNotConnected;
        return bcmErrNotConnected;
    }

    /* Wait for it */
    if (msg->trHdr)
        bcmOsSemGet(&msg->trHdr->sem);

    /* Release transport header */
    bcmOsMutexLock(&tr->mutex);
    if (msg->trHdr)
    {
        _bcmTrHdrFree(tr, msg->trHdr, &tr->msgList);
        msg->trHdr = NULL;
    }
    bcmOsMutexUnlock(&tr->mutex);

    /* Got response or timeout */
    return msg->status;
}

/** Release message
 *
 * \param[in]   msg     msg returned by bcmMsgWaitResponse() or bcmMsgReceive()
 */
void bcmMsgFree(bcmMsg *msg)
{
    if (*(msg->response))
        bcmOsFree(*(msg->response));
}

/* Check for receive and timeouts */
int bcmMsgRxPoll(bcmOltIdx olt, U16 channel)
{
    bcmTransport *tr = NULL;

    if ((channel & bcmTrChannelConfig))
        tr = transports[olt][bcmChIdxConfig];
    else if ((channel & bcmTrChannelAuto))
        tr = transports[olt][bcmChIdxAuto];

    if (!tr)
        return bcmErrNotConnected;

    return _bcmTrPoll(tr);
}

/** Register autonomous message handler
 * \param[in]   handler Autonomous message handler.
 *                      The handler is called in the context of RX_THREAD associated with
 *                      per-OLT autonomous transport channel.
 * \param[in]   flags   Registration flags - a combination of \ref bcmAutoMsgFlags bits\n
 *                      If \ref bcmAutoMsgFlag_Keep is not set, emmiMsg is released automatically
 *                      upon return from the "handler" callback
 * \return 0=success or error code
 */
bcmErrno bcmMsgHandlerRegister(F_bcmAutoHandler handler, U32 flags)
{
    if (autoHandler && handler)
        return bcmErrAlreadyConnected;
    autoHandler = handler;
    autoFlags = flags;
    return bcmErrOk;
}

/** Unregister autonomous message handler
 * \param[in]   handler Autonomous message handler registered by bcmAutoHandlerRegister
 * \return 0=success or error code
 */
bcmErrno bcmMsgHandlerUnregister(void *handler)
{
    autoHandler = NULL;
    autoFlags = 0;
    return bcmErrOk;
}

/*
 * External transport interface
 */

/* Open transport channel */
bcmErrno bcmTrOpen(bcmOltIdx olt, U16 channel, bcmTrCfg *parm, bcmTrDriver *driver)
{
    bcmTransport *tr;
    bcmErrno rc = bcmErrOk;

    if (olt >= BCM_TR_MAX_OLTS)
        return bcmErrParm;

    /* Make sure that not configured yet */
    if (((channel & bcmTrChannelConfig) && transports[olt][bcmChIdxConfig]) ||
        ((channel & bcmTrChannelAuto) && transports[olt][bcmChIdxAuto]) )
    {
        return bcmErrAlreadyConnected;
    }

    /* Validate parameters */
    if (!parm)
    {
        return bcmErrParm;
    }

    /* Validate transport driver */
    if ((parm->type != bcmTrTypeUdp) &&
        (!driver || !driver->open || !driver->close || !driver->send || !driver->recv))
    {
        return bcmErrParm;
    }

    /* Allocate */
    tr = bcmOsCalloc(sizeof(*tr));
    if (!tr)
        return bcmErrNoMemory;

    snprintf(tr->name, sizeof(tr->name), "bcmTr_%u_%u", olt, channel);
    tr->cfg = *parm;
    if (driver)
        tr->driver = *driver;
    else
    {
        /* Built-in UDP transport */
        tr->driver.open = bcmUdpTransportOpen;
        tr->driver.close = bcmUdpTransportClose;
        tr->driver.send = bcmUdpTransportSend;
        tr->driver.recv = bcmUdpTransportRecv;
    }
    TAILQ_INIT(&tr->freeReqList);
    TAILQ_INIT(&tr->freeAutoList);
    TAILQ_INIT(&tr->msgList);
    bcmOsMutexInit(&tr->mutex);

    /* Set defaults */
    if (!tr->cfg.maxRetries)
        tr->cfg.maxRetries = BCM_TR_MAX_RETRIES;
    if (!tr->cfg.msgTimeout)
        tr->cfg.msgTimeout = BCM_TR_MSG_TIMEOUT;
    if (!tr->cfg.maxFragments)
        tr->cfg.maxFragments = BCM_TR_MAX_FRAGMENTS;
    if (!tr->cfg.maxRequests)
        tr->cfg.maxRequests = BCM_TR_MAX_REQUESTS;
    if (!tr->cfg.maxAutos)
        tr->cfg.maxAutos = BCM_TR_MAX_AUTOS;
    if (!tr->cfg.maxMtuSize)
        tr->cfg.maxMtuSize = BCM_TR_MAX_MTU_SIZE;
    if (!tr->cfg.msgWaitTimeout)
        tr->cfg.msgWaitTimeout = BCM_TR_MSG_WAIT_MS;
    if (!tr->cfg.msgReadyTimeout)
        tr->cfg.msgReadyTimeout = BCM_TR_MSG_READY_MS;
    tr->periodTimeOutCheck = tr->cfg.msgWaitTimeout;
    tr->lastTimeOutCheck = bcmOsGetCurrentTimeMs();

    /* Allocate and initialize transport blocks and put onto free request and autonomous lists */
    rc = _bcmTrHdrListAlloc(tr);
    if (rc)
        goto cleanup;

    /* Open/connect on driver level */
    rc = tr->driver.open(tr);
    if (rc)
        goto cleanup;

    tr->connected = 1;

    /* Create rx thread if necessary.
     */
    if (tr->cfg.rxThreadPriority >= 0)
    {
        rc = bcmOsThreadCreate(&tr->rxThread, tr->cfg.rxThreadPriority,
            _bcmTrRxThreadHandler, tr, BCM_TR_RX_THREAD_STACK, tr->name);
    }
    if (rc)
    {
        tr->driver.close(tr);
        goto cleanup;
    }
    if ((channel & bcmTrChannelConfig))
        transports[olt][bcmChIdxConfig] = tr;
    if ((channel & bcmTrChannelAuto))
        transports[olt][bcmChIdxAuto] = tr;
    tr->channel = channel;

    return bcmErrOk;

cleanup:
    _bcmTrHdrListFree(tr);
    bcmOsFree(tr);
    return rc;
}

/** Close transport channel */
bcmErrno bcmTrClose(bcmOltIdx olt, U16 channel)
{
    bcmTransport *tr = NULL;

    if ((channel & bcmTrChannelConfig))
        tr = transports[olt][bcmChIdxConfig];
    else if ((channel & bcmTrChannelAuto))
        tr = transports[olt][bcmChIdxAuto];

    /* Make sure that channel mask matches transport */
    if (!tr || tr->channel != channel)
        return bcmErrParm;

    /* Kill rx thread if any */
    if (tr->cfg.rxThreadPriority >= 0)
    {
        tr->kill_request = 1;
        while(!tr->kill_done)
            bcmOsSleep(1);
        bcmOsThreadDestroy(tr->rxThread);
    }

    /* Close connection */
    if (tr->driver.close)
        tr->driver.close(tr);

    /* Release all pending messages */
    _bcmTrHdrListFree(tr);

    /* Unregister & release */
    if ((channel & bcmTrChannelConfig))
        transports[olt][bcmChIdxConfig] = NULL;
    if ((channel & bcmTrChannelAuto))
        transports[olt][bcmChIdxAuto] = NULL;

    bcmOsMutexDestroy(&tr->mutex);
    bcmOsFree(tr);

    return bcmErrOk;
}

/** Get transport statistics */
bcmErrno bcmTrStatGet(bcmOltIdx olt, U16 channel, bcmTrStat *stat)
{
    bcmTransport *tr = NULL;

    if ((channel & bcmTrChannelConfig))
        tr = transports[olt][bcmChIdxConfig];
    else if ((channel & bcmTrChannelAuto))
        tr = transports[olt][bcmChIdxAuto];

    if (!tr)
        return bcmErrNotConnected;
    if (!stat || tr->channel != channel)
        return bcmErrParm;

    *stat = tr->stat;

    return bcmErrOk;
}
