from typing import List, Literal, Dict, Union, Tuple, Type, Any
from operator import itemgetter
from datetime import datetime

from numpy import array
# import pandas as pd
import networkx as nx

# import plotly
# import plotly.express as px
# import plotly.graph_objects as go
import plotly
from plotly import (
    express as px,
    graph_objects as go
)

from app.constants import NO_DATE
from app.models import Change


COLORS = {
    'synt': "#636efa",
    'sem': "#EF553B"
}

BASE_TYPES = Union[str, int, float]
JSON = Union[
    BASE_TYPES,
    Dict[BASE_TYPES, Union[BASE_TYPES, List['JSON']]],
    List[Union[BASE_TYPES, List['JSON']]]
]


class BaseChangesPlot:
    """Base class for changes plots"""
    def __init__(self, *args, **kwargs): ...
    def __add__(self, other): ...
    def process_dates(self): ...
    def finalize(self): ...

    @classmethod
    def from_elements(cls, elements: Union[List[Any], Dict[str, Any]], **kwargs): ...

    def to_plotly_obj(self) -> go.Figure: ...
    def to_plotly_json(self) -> JSON: return self.to_plotly_obj().to_json()

    def to_plotly_image(self, name, format='png') -> None:
        self.to_plotly_obj().write_image(name.format(format))

    # def __getattribute__(self, __name: str) -> Any:
    #     print(f"fetching {__name}")
    #     return super().__getattribute__(self, __name)


class ConstructionChangesPlot(BaseChangesPlot):
    """Plot of a single construction"""
    def __init__(
        self, no_last_date_option: Literal['current' or 'largest'] = 'largest',
        plot_rgba: Tuple[int, int, int, float] = (190,80,120,.03),
        use_one_legend_entry_per_name=True,
        add_transparent_early_late=True,
    ):
        super().__init__()

        self.no_last_date_option = no_last_date_option
        this_year = datetime(datetime.now().year, 1, 1)
        self.last_date = (this_year
                          if no_last_date_option == 'current' else None)

        self.name2num = {}
        self.name2bar_indices = {}
        # whether to allow only one trace from the group to appear in legend
        self.use_one_legend_entry_per_name = use_one_legend_entry_per_name

        # to add transparent bars on ends
        self.add_transparent_early_late = add_transparent_early_late
        self.min_date = self.MIN_DATE = datetime(1800, 1, 1)
        self.max_date = self.MAX_DATE = this_year
        self.TRANSP_OPACITY = 0.4

        self.elements = {}
        self.bars = []

        self.layout = {
            'barmode': 'overlay',
            'hovermode': 'closest',
            # 'paper_bgcolor': 'rgba(0,0,0,0)',
            # 'plot_bgcolor': 'rgba(190,80,120,.03)',
            'legend': {'title': {'text': 'Уровень'}, 'tracegroupgap': 0},
            'margin': {'t': 15, 'b': 0, 'l': 0, 'r': 0},
            'autosize': False,
            'xaxis': {
                # 'anchor': 'y', 'domain': [0.0, 1.0],
                'type': 'date', 'title': {'text': 'Год'},
                'range': [self.MIN_DATE, self.MAX_DATE],
                'showgrid': True, 'zeroline': False,
            },
            'yaxis': {
                'anchor': 'x', 'domain': [0.0, 1.0],
                'range': [0.9, 1.1],
                'showgrid': False, 'zeroline': False, 'visible': False,
            }
        }

    def get_largest_date(self):
        data = self.elements

        self.last_date = max(_date for level in data
                             for _date in data[level]['last_attested']
                             if _date is not NO_DATE)

    def get_smallest_date(self):
        data = self.elements
        self.first_date = min(_date for level in data
                              for _date in data[level]['first_attested']
                              if _date is not NO_DATE)

    def process_dates(self):
        # elements = self.elements
        last_date = self.last_date
        if not last_date:
            raise ValueError

        for level, level_data in self.elements.items():
            last_dates = level_data['last_attested']
            first_dates = level_data['first_attested']

            corrected_last_dates = []

            for i, last_date_ in enumerate(last_dates):
                if last_date_ is NO_DATE and first_dates[i] is NO_DATE:
                    # remove first_date and don't add last_date
                    first_dates.pop(i)
                    continue
                elif last_date_ is NO_DATE:
                    last_date_ = last_date

                corrected_last_dates.append(last_date_)

            self.elements[level]['last_attested'] = corrected_last_dates

    def _add_interval(
        self, first_date_: datetime, last_date_: datetime, level: str, j: int,
        opacity=None, different_hover=None, pop: List[str]=None, showlegend=True
    ):
        if last_date_ is NO_DATE or first_date_ is NO_DATE:
            print(first_date_, last_date_)
            return

        _x = (last_date_ - first_date_).total_seconds() * 1000

        dir = {'synt': -1, 'sem': 1}[level]
        print(level, self.name2num)
        max_offset = -0.01 * (self.name2num.get(level, 3))
        offset = dir * (max_offset + j * 0.01)  # former max_offset = -0.03
        print(offset)

        bar = {
            'alignmentgroup': 'True',
            'base': array(first_date_, dtype=object),
            # 'base': array(first_date_, ),
            # 'customdata': level,
            'name': level,
            # 'text': (
            #     f'{first_date_}-{last_date_}'
            # ),
            'legendgroup': level,
            'marker': {'color': COLORS[level], 'opacity': 0.6},
            'offset': offset,
            'width': 0.01,
            'offsetgroup': level,
            'orientation': 'h',
            'showlegend': showlegend,
            'textposition': 'auto',
            # 'x': array(x),
            'x': array(_x),
            'xaxis': 'x',
            # 'y': array([1, 1, 1, 1], dtype='int64'),
            'y': array(1),
            'yaxis': 'y',
            # some attributes have `data.` prepended as per:
            #   https://stackoverflow.com/questions/66119369/custom-data-in-plotly-tooltip-not-showing
            #   https://plotly.com/python/reference/bar/#bar-hovertemplate
            #   https://plotly.com/javascript/plotlyjs-events/#event-data
            'hovertemplate': (
                'Тип: %{data.name}<br>'
                'Первое вхождение: %{data.base|%Y}<br>'
                'Последнее вхождение: %{x|%Y}<br>'
                'Номер конструкции: %{y}'
                '<extra></extra>'
            ),
        }
        if opacity:
            bar["opacity"] = opacity
        if different_hover:
            bar["hovertemplate"] = different_hover

        if pop:
            for key_to_remove in pop:
                bar.pop(key_to_remove)

        self.bars.append(bar)

        print("added bar")

    def make_bars(self) -> None:
        if self.first_date is not NO_DATE and self.first_date < self.MIN_DATE:
            min_date = self.first_date
        else:
            min_date = self.MIN_DATE
        print(self.MIN_DATE, self.first_date, min_date)
        # min_date = min(self.MIN_DATE, self.first_date)
        if self.last_date is not NO_DATE and self.last_date > self.MAX_DATE:
            max_date = self.last_date
        else:
            max_date = self.MAX_DATE
        # max_date = max(self.MAX_DATE, self.last_date)

        self.min_date = min_date
        self.max_date = max_date

        for i, (level, level_data) in enumerate(self.elements.items()):
            for j, (first_date_, last_date_) in enumerate(
                    zip(level_data['first_attested'], level_data['last_attested'])
            ):
                if last_date_ is NO_DATE or first_date_ is NO_DATE:
                    continue

                if (not isinstance(first_date_, datetime)
                    or not isinstance(last_date_, datetime)
                ):
                    continue

                print(level, level_data)

                self._add_interval(first_date_, last_date_, level, j)
                if self.add_transparent_early_late:
                    args = dict(
                        opacity=self.TRANSP_OPACITY, # pop=[],
                        different_hover="Тип: %{data.name}<br><нет данных>",
                        showlegend=False)

                    self._add_interval(
                        min_date, first_date_, level, j, **args)
                    self._add_interval(
                        last_date_, max_date, level, j, **args)

    # def __add__(self, other):

    @classmethod
    def from_elements(
        cls, elements: Dict[str, Dict[str, List[datetime]]], *args, **kwargs
    ):
        construction = ConstructionChangesPlot(*args, **kwargs)
        construction.elements = elements

        construction.num_elements = len(elements)
        construction.count_data_in_name()
        print(construction.name2num)
        # construction.make_name2bar_indices()/
        print("added elements, counted data by name")

        construction.get_largest_date()
        construction.get_smallest_date()

        construction.process_dates()
        print("processed dates")

        construction.make_bars()

        print(f"made bars")

        min_date = construction.min_date
        max_date = construction.max_date

        construction.layout["xaxis"]["range"] = [min_date, max_date]

        print("updated xaxis dates")

        return construction

    def count_data_in_name(self) -> Dict[str, int]:
        name2num = {}
        for name, changes in self.elements.items():
            # any of `first_attested`, `last_attested` should do
            name2num[name] = len(changes.get("first_attested", []))

        self.name2num = name2num
        return name2num

    def make_name2bar_indices(self) -> Dict[str, List[int]]:
        name2bar_indices = {}
        for i, bar in enumerate(self.bars):
            name = bar["name"]
            name2bar_indices.setdefault(name, []).append(i)

        print(f"calculated name2bar_indices:\n{name2bar_indices}")

        self.name2bar_indices = name2bar_indices
        return name2bar_indices

    def limit_one_legend_entry_per_name(self):
        if not self.name2bar_indices:
            self.make_name2bar_indices()

        print(f"name2bar_i:\n{self.name2bar_indices}")

        for name, bar_indices in self.name2bar_indices.items():
            bar_indices_to_hidelegend = bar_indices[1:]
            for bar_i in bar_indices_to_hidelegend:
                self.bars[bar_i]["showlegend"] = False

    def to_plotly_obj(
        self, layout: Dict[str, Union[str, int]] = None
    ) -> go.Figure:
        figure = go.Figure(layout=layout or self.layout)

        if self.use_one_legend_entry_per_name:
            self.limit_one_legend_entry_per_name()

        for bar in self.bars:
            # print(bar)
            figure.add_bar(**bar)

        return figure


class ConstructionComparisonChangesPlot(BaseChangesPlot):
    """Plot comparing a number of constructions
    """
    def __init__(self):
        super().__init__()

        self.constructions = []

    @classmethod
    def from_elements(cls, elements: List[Any], **kwargs):
        comparison = cls()
        for construction_desc in elements:
            construction = ConstructionChangesPlot.from_elements(construction_desc)
            comparison.constructions.append(construction)


class ConstructionSequentialChangesPlot(BaseChangesPlot):
    feats_to_check = ("stage", "level", "type_of_change",
                      "first_attested", "last_attested")

    def __init__(self, nodes: List=None, edges=None, graph: nx.Graph = None):
        super().__init__()

        self.nodes = nodes
        self.edges = edges

        self.graph = graph

        self.layout = dict(
            title='<br>Последовательность изменений',
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            # annotations=[dict(
            #     text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
            #     showarrow=False,
            #     xref="paper", yref="paper",
            #     x=0.005, y=-0.002)],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )

    @staticmethod
    def model2node(element, feats_to_check):
        attrs = {feat: getattr(element, feat) for feat in feats_to_check}
        node = (element.id, attrs)
        return node

    @classmethod
    def from_elements(cls, elements: List[Change], **kwargs):
        graph = nx.Graph()
        for element in elements:
            node = cls.model2node(element, cls.feats_to_check)
            graph.add_node(node)

            for next_change in element.next_changes:
                next_change_node = cls.model2node(next_change, cls.feats_to_check)
                graph.add_node(next_change_node)
                graph.add_edge(node, next_change_node)

        return cls(graph=graph)

    def add_all(self, G: nx.Graph):
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

    def to_plotly_obj(
        self, layout: Dict[str, Union[str, int]] = None
    ) -> go.Figure:
        figure = go.Figure(layout=layout or self.layout)

        for item in self.items:
            print(item)
            figure.add_bar(**item)

        return figure
