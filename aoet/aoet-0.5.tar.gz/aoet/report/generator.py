import aoet
import aoet.analysis.pca as pca
from aoet import logger, DATA_FILE

from shutil import copyfile

import pandas as pd
import numpy as np
import json
import os


def to_report(matrix, raw_data_dir, uniques, out, labels, core_samples, n_clusters, outliers):
    cols = ['x', 'y', 'label']
    if matrix.shape[1] > 2:
        try:
            matrix = pca.pca_projection(matrix)
        except np.linalg.LinAlgError as e:
            logger.exception(e)
            logger.warn(matrix)
            raise e
    elif matrix.shape[1] == 1:
        cols = ['x']
    elif matrix.shape[1] == 0:
        logger.error("No data to output!")
        return

    if not os.path.exists(out):
        os.makedirs(out)

    with open(os.path.abspath(os.path.join(raw_data_dir, aoet.REQUESTS_FILE))) as fp:
        req = np.array(json.load(fp))[uniques]
    with open(os.path.join(raw_data_dir, aoet.PRD_FILE)) as fp:
        prd = np.array(json.load(fp))[uniques]
    with open(os.path.join(raw_data_dir, aoet.TST_FILE)) as fp:
        tst = np.array(json.load(fp))[uniques]

    with open(os.path.abspath(os.path.join(out, aoet.REQUESTS_FILE)), 'w') as fp:
        json.dump(req.tolist(), fp)
    with open(os.path.join(out, aoet.PRD_FILE), 'w') as fp:
        json.dump(prd.tolist(), fp)
    with open(os.path.join(out, aoet.TST_FILE), 'w') as fp:
        json.dump(tst.tolist(), fp)
    with open(os.path.join(out, 'stats.json'), 'w') as fp:
        json.dump({'labels': labels.tolist(), 'clusters': n_clusters, 'outliers': outliers, 'core_samples': core_samples}, fp)

    frame = pd.DataFrame(np.hstack((matrix, labels.reshape(matrix.shape[0], 1))), columns=cols)

    with open(os.path.join(out, DATA_FILE), 'w') as fp:
        fp.write(frame.to_json(orient='records'))

    copyfile(os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources', 'results.html')),
             os.path.join(out, 'results.html'))

    text = "Results: {} clusters and {} outliers. \n".format(n_clusters, outliers)
    for i in range(n_clusters):
        text += '-' * 60 + '\n'
        text += 'Cluster {}, most typical example: \n'.format(i)
        text += ">>> Request"
        text += json.dumps(req[core_samples[i]], indent=2, ensure_ascii=False)
        text += "\n <<< PRD \n"
        text += json.dumps(prd[core_samples[i]], indent=2, ensure_ascii=False)
        text += "\n <<< TST \n"
        text += json.dumps(tst[core_samples[i]], indent=2, ensure_ascii=False)
        text += '\n' + '-' * 60 + '\n'

    logger.info(text)
    with open(os.path.join(out, 'overview.txt'), "w") as text_file:
        text_file.write(text)