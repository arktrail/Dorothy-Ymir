from fasttext import load_model
import sys
import errno

if __name__ == "__main__":
    f = load_model(sys.argv[1])
    out_path = sys.argv[2]

    counter = 0
    
    with open(out_path, "w") as out_file:
        words = f.get_words()
        out_file.write(str(len(words)) + " " + str(f.get_dimension()) + "\n")
        for w in words:
            v = f.get_word_vector(w)
            vstr = ""
            for vi in v:
                vstr += " " + str(vi)
            try:
                out_file.write(w + vstr + "\n")
                if counter % 10000 == 0:
                    print(counter)
                counter += 1
            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass
