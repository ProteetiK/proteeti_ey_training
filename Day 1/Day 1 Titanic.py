import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
print('Numpy version: ', np.__version__)

df = sns.load_dataset('titanic')
missing = df.isnull().sum()
missing_percent = 100 * missing / len(df)
pd.DataFrame({'missing': missing, 'missing_percent': missing_percent.round(2)}).sort_values(by='missing', ascending=False)

#Task o
#1. How many unique values in 'embarked'?
print('Unique EMbarked: ', df['embarked'].nunique())
#2. What is the most common passenger class?
print('Most frequent pclass: ', df['pclass'].mode()[0])

df2 = df.copy()
df2['age'] = df2['age'].fillna(df2['age'].mean())
df2['embarked'] = df2['embarked'].fillna(df2['embarked'].mode()[0])
df2 = df2.drop(columns=['deck'])

#Task 1: Find all male passengers who paid a fare of above 200 and survived
print('Task 1')
print(df2[(df2['sex']=='male') & (df2['alive']=='yes')])
#Task 2: eUsing .iloc extract rows 100 to 109 and the last 3 columns
print()
print('Task 2')
print(df2.iloc[100:110, -3:])

#Task 3: Mean fare for each embark town
print(df2.groupby('embark_town')['fare'].mean())
#Task 4: Survivor count sorted by Class
print(df2[df2['alive']=='yes'].groupby('pclass').size().sort_values(ascending=False))

#Task 5: Merging Embarkment Port Full names with codes
port_lookup = pd.DataFrame({'embarked':['C', 'Q', 'S'], 'full_name': ['Chebourg', 'Queenstown', 'Southampton']})
df_merged = df2.merge(port_lookup, on='embarked', how='left')
print('Task 5')
print(df_merged[['embarked', 'full_name']].drop_duplicates())
print(df_merged.head())

plt.rcParams['figure.dpi'] = 120
sns.set_theme(style='whitegrid', palette='muted')

df = sns.load_dataset('titanic').dropna(subset=['age', 'embarked'])
df['age_group'] = pd.cut(df['age'], bins=[0,12,18,35,60,120], labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Senior'])
print("DF Shape: ", df.shape)

fig,ax = plt.subplots(figsize=(7,4))
#Task 1: Bar Plot
sns.barplot(data=df, x='pclass', hue='sex', y='survived')
ax.set_title('Survival rate by passenger class', pad=12)
ax.set_xlabel('Passenger Class')
ax.set_ylabel('Survival Rate')
ax.set_ylim(0,1)
plt.savefig('graph task 1.png')
plt.show()

#Task 2: Dashboard
fig,axes = plt.subplots(3, 2, figsize=(14,10))
fig.suptitle('Titanic Passenger Data - A visual Story', fontsize=16, fontweight='bold', y=1.01)
ax = axes[0,0]
surv = df.groupby('pclass')['survived'].mean()
ax.bar(['1st', '2nd', '3rd'], surv.values, color=['#1565C0', '#1976D2', '#90CAF9'])
ax.set_title('A. Survival rate by class')
ax.set_ylabel('Rate')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y,_: f'{y:.0%}'))

ax = axes[0,1]
ax.hist(df[df['survived']==0]['age'], bins=25, alpha=0.6, color='#E53935', label='Not survived')
ax.hist(df[df['survived']==1]['age'], bins=25, alpha=0.6, color='#43A047', label='Survived')
ax.set_title('B. Distribution by outcome')
ax.set_xlabel('Age')
ax.set_ylabel('Count')
ax.legend(fontsize=8)

ax = axes[1,0]
for cls, c, lbl in zip([1,2,3], ['#1976D2', '#43A047', '#E53935'],['1st', '2nd', '3rd']):
    s = df[df['pclass']==cls]
    ax.scatter(s['age'], s['fare'], c=c, alpha=0.4, s=20, label=lbl)
ax.set_yscale('log')
ax.set_title('C. Fare vs age (log scale)')
ax.set_xlabel('Age')
ax.set_ylabel('Fare (log)')
ax.legend(title='Class', fontsize=8)

ax = axes[1,1]
pivot = df.pivot_table(values='survived', index='pclass', columns='embarked', aggfunc='mean')
sns.heatmap(pivot, annot=True, fmt='.0%', cmap='RdYlGn', linewidth=0.5, ax=ax, vmin=0, vmax=1, cbar=False)
ax.set_title('D. Survival rate: class c port')
ax.set_xlabel('Port')
ax.set_ylabel('Class')

ax = axes[2,0]
sns.countplot(data=df, x='age_group', hue='sex', ax=ax)
ax.set_title('E. Age distribution by sex')
ax.set_xlabel('Age')
ax.set_ylabel('Number of Passengers')
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('titanic_dashboard.png')
plt.show()

