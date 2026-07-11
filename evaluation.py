from sklearn.metrics import confusion_matrix

# Example counts
true_positive = 50
false_positive = 5
true_negative = 45
false_negative = 3

print("False Positive Rate:")
fpr = false_positive / (false_positive + true_negative)
print(fpr)

print("False Negative Rate:")
fnr = false_negative / (false_negative + true_positive)
print(fnr)