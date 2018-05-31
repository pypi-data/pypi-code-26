import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class DataExplorer(object):
	def __init__(self, label_tag, problem="classification"):
		super(DataExplorer, self).__init__()
		self.label_tag = label_tag
		self.problem = problem

	def first_exploration(self, df, rows=5):
		
		print("First %s Rows of the dataset." %rows)
		print(df.head(rows))
		print("Last %s Rows of the dataset." %rows)
		print(df.head(rows))
		
		if self.problem == "classification":
			print("Number of samples for each target")
			target = pd.Series(df[self.label_tag])
			print(target.value_counts())
		else:
			print("Target MEAN %s, STD %s " %(df[self.label_tag].mean(), df[self.label_tag].std()))
			sns.distplot(df[self.label_tag])
			plt.show()
		return

	def features_correlation(self, df, width=25, height=12):
		colormap = plt.cm.RdBu
		plt.figure(figsize=(width, height))
		plt.title('Pearson Correlation of Features', y=1.05, size=15)
		sns.heatmap(df.astype(float).corr(), cmap=colormap)
		plt.show()
		return

	def pair_plots(self, df):
		g = sns.pairplot(df, hue=self.label_tag)
		g.set(xticklabels=[])
		plt.show()
		return

	def pair_plots_kde(self, df):
		g = sns.PairGrid(df)
		g.map_diag(sns.kdeplot)
		g.map_offdiag(sns.kdeplot, cmap="Blues_d", n_levels=6)
		plt.show()
		return

	def plot_features_distribution(self, df, rows=4, height=13, width=25):
		features = df.columns
		columns = int(len(features)/rows) + 1
		fig = plt.figure(figsize=(width, height))
		for i, feat_name in enumerate(features):
			ax = fig.add_subplot(rows, columns, i+1)
			sns.distplot(df[feat_name], ax=ax)
		plt.show()
		return

	def plot_features_box_plot(self, df, rows=4, height=13, width=25):
		features = df.columns
		columns = int(len(features)/rows) + 1
		fig = plt.figure(figsize=(width, height))
		for i, feat_name in enumerate(features):
			ax = fig.add_subplot(rows, columns, i+1)
			sns.boxplot(y=df[feat_name], ax=ax)
		plt.show()
		return

		