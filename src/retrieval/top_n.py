import math

from .ner_retriever import NER_Retriever
from .retrieval_method import RetrievalMethod
from drqa import retriever
from drqascripts.retriever.build_tfidf_lines import OnlineTfidfDocRanker


class TopNDocsTopNSents(RetrievalMethod):

    class RankArgs:
        def __init__(self):
            self.ngram = 2
            self.hash_size = int(math.pow(2,24))
            self.tokenizer = "simple"
            self.num_workers = None

    def __init__(self,db,n_docs,n_sents,whole_docs,compat,model):
        super().__init__(db)
        self.n_docs = n_docs
        self.n_sents = n_sents
        self.whole_docs = whole_docs
        self.compat = compat
        self.ranker = retriever.get_class('tfidf')(tfidf_path=model)
        self.onlineranker_args = self.RankArgs()

        self.doc_titles = [self.ranker.get_doc_id(i) for i in range(self.ranker.num_docs)]
        self.ner_retriever = NER_Retriever(self.doc_titles)

    def get_docs_for_claim(self, claim_text):
        doc_names, doc_scores = self.ranker.closest_docs(claim_text, self.n_docs)
        return zip(doc_names, doc_scores)


    def tf_idf_sim(self, claim, lines, freqs=None):
        tfidf = OnlineTfidfDocRanker(self.onlineranker_args, [line["modified_sentence"] for line in lines], freqs)
        line_ids, scores = tfidf.closest_docs(claim,self.n_sents)
        ret_lines = []
        for idx, line in enumerate(line_ids):
            ret_lines.append(lines[line])
            ret_lines[-1]["score"] = scores[idx]
        return ret_lines


    def ner_page_recommendations(self, claim_text):
        return self.ner_retriever.lookups(claim_text)

    def get_sentences_for_claim(self,claim_text,include_text=False):
        pages = self.get_docs_for_claim(claim_text)
        sorted_p = list(sorted(pages, reverse=True, key=lambda elem: elem[1]))
        pages = [p[0] for p in sorted_p[:self.n_docs]]
        for page in self.ner_page_recommendations(claim_text):
          # print("Adding NER page for claim: " + page + " " + claim_text)
          if(page not in pages):
            pages.append(page)

        p_lines = []
        first_lines = []
        for page in pages:
            lines = self.db.get_doc_lines(page)
            lines = [line.split("\t")[1] if len(line.split("\t")) > 1 else "" for line in
                     lines.split("\n")]

            if self.whole_docs:
                lines = lines[:self.n_sents]

            p_lines.extend(zip(lines, [page] * len(lines), range(len(lines))))
            if(len(lines) > 0):
                first_lines.append({"sentence": lines[0],
                                    "page": page,
                                    "line_on_page": 0,
                                    "modified_sentence": "[ " + page + " ] " + lines[0],
                                    "score": 1
                                   })
        first_lines = first_lines[:self.n_docs]


        lines = []
        for p_line in p_lines:
            title = p_line[1]
            title = title.replace("_", " ")
            lines.append({
                "sentence": p_line[0],
                "page": p_line[1],
                "line_on_page": p_line[2],
                "modified_sentence": "[ " + title + " ] " + p_line[0]
            })

        if self.whole_docs:
            return [(s["page"], s["line_on_page"]) for s in lines]

        else:
            scores = self.tf_idf_sim(claim_text, lines)

            if(len(scores) == 0 and self.compat == False):
                scores = first_lines   # in case TFIDF fails to pick sentences

            if include_text:
                return scores

            return [(s["page"], s["line_on_page"]) for s in scores]

