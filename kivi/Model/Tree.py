

from sklearn.tree import DecisionTreeRegressor, export_graphviz
from sklearn.metrics import mean_squared_error

class Tree:

    def __init__(self, data, y_name):
        """

        :param data:
        :param y_name:
        """

        y = data.pop(y_name)
        self.exog = data.copy()
        self.endog = y.copy()
        self.cols_name = self.exog.columns.to_list()


    def fit(
            self,
            max_depth=2,
            min_samples_split=500,
            min_samples_leaf=50,
    ):
        """

        :param max_depth:
        :param min_samples_split:
        :param min_samples_leaf:
        :return:
        """

        self.model = DecisionTreeRegressor(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
        ).fit(self.exog, self.endog)


    def metrics(self, ):
        """

        :return:
        """
        self.bad_rate = self.endog.sum() / self.endog.count()
        self.mse = mean_squared_error(self.endog, self.model.predict(self.exog))


    def plot_tree(self, class_names=['no', 'yes']):
        """
        Des:
        :param feature_names:
        :param class_names:
        :return:
        """
        import pydot
        from IPython.display import Image
        from sklearn.externals.six import StringIO

        dot_data = StringIO()

        export_graphviz(
            self.model,
            out_file=dot_data,
            feature_names=self.cols_name,
            class_names=class_names,
            filled=True,
            rounded=True,
            special_characters=True,
            proportion=True,
        )

        (graph,) = pydot.graph_from_dot_data(dot_data.getvalue())
        return Image(graph.create_png())

