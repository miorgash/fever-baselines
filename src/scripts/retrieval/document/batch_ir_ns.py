import argparse
import json
from tqdm import tqdm
from drqa import retriever
from drqa.retriever import DocDB


def process(ranker, query, k=1):
    doc_names, doc_scores = ranker.closest_docs(query, k)

    return doc_names



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default=None)
    parser.add_argument('--count',type=int, default=1)
    parser.add_argument('-i', '--in-file', type=str)
    parser.add_argument('-o', '--out-file', type=str)
    args = parser.parse_args()

    k = args.count
    ranker = retriever.get_class('tfidf')(tfidf_path=args.model)
    in_file = args.in_file
    out_file = args.out_file

    with open(in_file, "r") as f:
        with open(out_file, "w+") as f2:
            for line in tqdm(f.readlines()):
                line = json.loads(line)

                if line["label"] == "NOT ENOUGH INFO":
                    pages = process(ranker, line['claim'], k=k)
                    pp = list(pages)

                    for idx,evidence_group in enumerate(line['evidence']):
                        for evidence in evidence_group:
                            if idx<len(pp):
                                evidence[2] = pp[idx]
                                evidence[3] = -1


                f2.write(json.dumps(line) + "\n")


