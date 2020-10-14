# Execution(jp)


自作コンテナ起動

```
docker run -it --rm --name fever-createdb \
    -v fever-data:/fever/data \
    -v fever-config:/fever/config \
    -v fever-logs:/fever/logs \
    miorgash/fever-baselines:latest
```

自作コンテナ内で実行

```
# IR preprocess
# create evidence db
PYTHONPATH=src python src/scripts/build_db.py data/evidence/input data/evidence/evidence.db

# create evidence tf-idf matrix in sqlite3 db
PYTHONPATH=src python src/scripts/build_tfidf.py data/evidence/evidence.db data/index/

# NLI preprocess; sampling evidences for the "Not Enough Info" claims
SPLIT=train
# SPLIT=dev
PYTHONPATH=src python src/scripts/retrieval/document/batch_ir_ns.py \
    --model data/index/evidence-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz \
    --count 1 \
    -i data/claim/input/${SPLIT}.jsonl \
    -o data/claim/${SPLIT}.ns.pages.p1.jsonl

```

オリジナルコンテナを起動（miorgash/fever-baselines では train\_da.py で allennlp バージョン起因のエラー発生のため）

```
sudo docker run -it --rm --name fever \
    -v fever-data:/fever/data \
    -v fever-config:/fever/config \
    -v fever-logs:/fever/logs \
    --gpus all \
    sheffieldnlp/fever-baselines
```

オリジナルコンテナ内で実行

```
# Train NLI Model
export CUDA_DEVICE=-1
export ALLENNLP_LOGS='/fever/logs/fever_nn_ora_sent_yumuseki' # example
PYTHONPATH=src python src/scripts/rte/da/train_da.py data/evidence/evidence.db config/fever_nn_ora_sent_kurohashi.json $ALLENNLP_LOGS --cuda-device $CUDA_DEVICE
cp $ALLENNLP_LOGS/model.tar.gz data/models/decomposable_attention.tar.gz

# IR
PYTHONPATH=src python src/scripts/retrieval/ir.py --db data/evidence/evidence.db --model data/index/fever-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --in-file data/claim/input/test.jsonl --out-file data/claim/test.sentences.p5.s5.jsonl --max-page 5 --max-sent 5

# NLI test
PYTHONPATH=src python src/scripts/rte/da/eval_da.py data/evidence/evidence.db data/models/decomposable_attention.tar.gz data/claim/test.sentences.p5.s5.jsonl  --log logs/decomposable_attention.test.log
```

### Trouble shooting for jp

```
# Train DA
# db 構築に用いた evidence の json テキストの文字コードと，batch_ir_ns.py によるサンプリング後の json テキストの文字コードが合致しない場合，
# RuntimeError: inconsistent tensor size, expected tensor [213 x 300] and src [210 x 300] to have the same number of elements, ... が発生

# [INFO] 2020-08-19 01:13:53,807 - allennlp.training.trainer - Ran out of patience.  Stopping training.
# https://github.com/benbogin/spider-schema-gnn/issues/5
# JSON の設定で patience を変更すれば OK

# Predict
# IR: evidence.db のテキストにおいて lines の区切り以外の箇所で \n が入っていると Index エラーが発生する．
```

# Files
```
- download-raw-wiki.sh         # Evidence の JSONL ファイルをダウンロード
+ process-wiki.sh              # Evidence の DB (sqlite) と tfidf を作成
- download-processed-wiki.sh   # Evidence の DB (sqlite) と tfidf をダウンロード
- download-data.sh             # Claim(Shared task 用全ファイル)ダウンロード
- download-shared-task-test.sh # Claim(Shared task 用 test データのみ)ダウンロード
- download-paper.sh            # Claim(論文データ)ダウンロード
- download-glove.sh            # GloVe 分散表現ダウンロード
- download-model.sh            # Model ダウンロード（DA）
```

