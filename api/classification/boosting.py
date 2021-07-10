from sklearn.ensemble import GradientBoostingClassifier

def gbt_clf(sample, data):
    clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,
        max_depth=1, random_state=0)
    clf.fit(data[0], data[1])
    return clf.predict(sample)[0]
    return 'boosting clf'