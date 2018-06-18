import matplotlib.pyplot as plt

fig = plt.figure('Picture from Bing')
img = plt.imread('BingWallpaper-2018-06-14.jpg')

_, ax = plt.subplots()
ax.imshow(img, cmap='gray')

ax.axis('off')

plt.show()

print(fig.get_dpi())