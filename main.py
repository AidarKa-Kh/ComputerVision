from roboflow import Roboflow

rf = Roboflow(api_key="D3omJYQMuNNVV3wqqwto")
project = rf.workspace().project("playing-cards-ow27d")
model = project.version(4).model

# infer on a local image
print(model.predict("https://goods-photos.static1-sima-land.com/items/3787362/0/1600.jpg?v=1647495785", hosted=True,
                    confidence=40, overlap=30).save("prediction.jpg"))

# visualize your prediction
# model.predict("your_image.jpg", confidence=40, overlap=30).save("prediction.jpg")

# infer on an image hosted elsewhere
# print(model.predict("URL_OF_YOUR_IMAGE", hosted=True, confidence=40, overlap=30).json())
