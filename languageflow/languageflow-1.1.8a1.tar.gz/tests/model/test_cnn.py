# -*- coding: utf-8 -*-
from unittest import TestCase, skip


@skip
class TestCNN(TestCase):

    def test_cnn(self):
        X = [
            "đồ ăn tốt",
            "món ăn thực sự rất ngon",
            "ngon thật",
            "giá rẻ",
            # NEGATIVE
            "chán cực kì",
            "phục vụ chán quá",
            "đồ uống chán lắm",
            "vệ sinh bẩn",
            "phục vụ còn quá kém",
            # NEUTRAL
            "cũng bình thường"
        ]
        y = ["POSITIVE", "POSITIVE", "POSITIVE", "POSITIVE",
             "NEGATIVE", "NEGATIVE", "NEGATIVE", "NEGATIVE", "NEGATIVE",
             "NEUTRAL"]
        from languageflow.model.cnn import KimCNNClassifier
        estimator = KimCNNClassifier()
        estimator.fit(X, y)

        X_test = [
            "chán",
            "tốt quá",
            "vệ sinh",
            "vệ sinh bẩn",
            "bẩn",
            "tôi thấy thái độ của nhân viên không tốt",
            "quán này rẻ nè"
        ]
        y_pred = estimator.predict(X_test)
        print("Test results")
        for i, x in enumerate(X_test):
            print("{} -> {}".format(x, y_pred[i]))
