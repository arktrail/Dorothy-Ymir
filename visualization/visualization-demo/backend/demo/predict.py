import fasttext

MODEL_PATH = "/home/ubuntu/model/fasttext/fasttext_model.bin"


def predict(predict_text: str):
    '''
    return: tuple(tuple(), np.array())
    '''
    model = fasttext.load_model(MODEL_PATH)
    res = model.predict(
        predict_text, k=-1, threshold=0.0)
    return res


if __name__ == "__main__":
    res = main("Which baking dish is best to bake a banana bread ?")
    print(res)
