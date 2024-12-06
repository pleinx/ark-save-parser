import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# Define the data
data = {
    'rating': [14.495094299316406, 3.344745397567749, 9.71588134765625, 5.116003036499023, 1.1281356811523438, 10.250511169433594],
    's1': [12324, 2298, 9150, 6250, 1125, 7960],
    's2': [16466, 4364, 11299, 6055, 2060, 13792]
}

# Create a DataFrame
df = pd.DataFrame(data)
print("Data:")
print(df)

# Descriptive statistics
print("\nDescriptive Statistics:")
print(df.describe())

# Pairplot to visualize relationships
sns.pairplot(df)
plt.show()

# Correlation matrix
corr_matrix = df.corr()
print("\nCorrelation Matrix:")
print(corr_matrix)

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.show()

# Features and target
X = df[['s1', 's2']]
y = df['rating']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the model
model = LinearRegression()

# Fit the model
model.fit(X_train, y_train)

# Coefficients
print("\nModel Coefficients:")
print(f"Intercept: {model.intercept_}")
print(f"s1 coefficient: {model.coef_[0]}")
print(f"s2 coefficient: {model.coef_[1]}")

# Predict on the test set
y_pred = model.predict(X_test)

# Compare actual vs predicted
comparison = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
print("\nActual vs Predicted:")
print(comparison)

# Calculate performance metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"\nMean Squared Error: {mse}")
print(f"R-squared: {r2}")

# Residual plot
residuals = y_test - y_pred
plt.scatter(y_pred, residuals)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Ratings')
plt.ylabel('Residuals')
plt.title('Residual Plot')
plt.show()

# Predicted vs Actual
plt.scatter(y_test, y_pred)
plt.xlabel('Actual Ratings')
plt.ylabel('Predicted Ratings')
plt.title('Actual vs Predicted Ratings')
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--')  # Line y=x
plt.show()
