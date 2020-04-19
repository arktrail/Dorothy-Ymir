import fasttext

MODEL_PATH = "/home/ubuntu/model/fasttext/fasttext_model.bin"

model = None


def load_model():
    global model
    print("start load model")
    model = fasttext.load_model(MODEL_PATH)
    print("the model has been loaded")


def predict(predict_text: str):
    '''
    return: tuple(tuple(), np.array())
    '''
    global model
    if model is None:
        print("model is not loaded yet, start load model")
        model = fasttext.load_model(MODEL_PATH)
    else:
        print("model is defined, do not need to be loaded")
    print("end load model, start prediction")
    res = model.predict(
        predict_text, k=-1, threshold=0.0)
    print("end predicting")
    return res


if __name__ == "__main__":
    res = main("Which baking dish is best to bake a banana bread ?")
    print(res)
