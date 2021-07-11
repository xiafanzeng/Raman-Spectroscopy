from sklearn.ensemble import RandomForestClassifier

def rf_clf(sample, data):   
    clf = RandomForestClassifier(n_estimators=10)
    clf.fit(data[0], data[1])
    return clf.predict(sample)[0]
    return 'rf clf'
