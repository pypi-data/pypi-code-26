

def load_pretrained_embedding(X, max_document_length, embedding_filename, embedding_dim):
    vocab_processor = learn.preprocessing.VocabularyProcessor(max_document_length)
    x = np.array(list(vocab_processor.fit_transform(x_text)))
    
    vocab_size = len(vocab_processor.vocabulary_)
    logging.info("Vocabulary Size: {:d}".format(vocab_size))
    
    embedding_w = np.random.uniform(-0.25,0.25, (vocab_size, embedding_dim))
    
    logging.info("Loading word2vec file {}\n".format(embedding_filename))
    with open(embedding_filename, "rb") as f:
        for line in f:
            row = line.strip().split(' ')
            assert len(row) == embedding_dim + 1, "invalid line: " + line
    
            idx = vocab_processor.vocabulary_.get(row[0])
            if idx == 0:
                continue
    
            embedding_w[idx] = np.fromstring(' '.join(row[1:]), dtype='float32', sep=' ')
    return x, embedding_w, vocab_processor
