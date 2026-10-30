import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\Users\saira\Downloads\employee.csv")

print("--- Employee Details ---")
print(df[['Name', 'Department', 'Salary']])
print("\n")

avg_salary_dept = df.groupby('Department')['Salary'].mean().reset_index()

print("--- Average Salary by Department ---")
print(avg_salary_dept)
print("\n")

plt.figure(figsize=(8, 5))
plt.bar(avg_salary_dept['Department'], avg_salary_dept['Salary'], color='skyblue', edgecolor='black')
plt.title('Average Employee Salary by Department')
plt.xlabel('Department')
plt.ylabel('Average Salary')
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()