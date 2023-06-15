from typing import List, Literal, Dict, Union, Tuple, Type, Any
from operator import itemgetter
from datetime import datetime

from numpy import array
import pandas as pd

# import plotly
# import plotly.express as px
# import plotly.graph_objects as go
import plotly
from plotly import (
    express as px,
    graph_objects as go
)

from app.constants import NO_DATE


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
            print(bar)
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


def new_plot_single_const_changes(
        data: Dict[str, Dict[str, List[datetime]]],
        no_last_date_option: Literal['current' or 'largest'] = 'largest'
):
    assert 1 <= len(data) <= 2 and ('synt' in data or 'sem' in data)

    # make a filler to be used instead of unmarked last-attested dates
    if no_last_date_option == 'largest':
        LAST_DATE = max(_date for level in data
                        for _date in data[level]['last_attested'])
    elif no_last_date_option == 'current':
        LAST_DATE = datetime(datetime.now().year, 1, 1)
    else:
        raise ValueError

    for level, level_data in data.items():
        last_dates = level_data['last_attested']
        first_dates = level_data['first_attested']

        corrected_last_dates = []

        for i, last_date_ in enumerate(last_dates):
            if last_date_ is NO_DATE and first_dates[i] is NO_DATE:
                # remove first_date and don't add last_date
                first_dates.pop(i)
                continue
            elif last_date_ is NO_DATE:
                last_date_ = LAST_DATE

            corrected_last_dates.append(last_date_)

        data[level]['last_attested'] = corrected_last_dates

    print(LAST_DATE, data, last_dates, corrected_last_dates, sep='\n')

    fig = go.Figure(
        layout={
            'barmode': 'overlay',
            # 'paper_bgcolor': 'rgba(0,0,0,0)',
            # 'plot_bgcolor': 'rgba(190,80,120,.03)',
            'legend': {'title': {'text': 'Уровень'}, 'tracegroupgap': 0},
            'margin': {'t': 60},
            # 'template': '...',
            'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0],
                      'type': 'date', 'title': {'text': 'Год'},
                      'showgrid': True, 'zeroline': False,
                      },
            'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0],
                      'showgrid': False, 'zeroline': False, 'visible': False,
                      }  # 'title': {'text': 'construction_id'}}
        }
    )

    for i, (level, level_data) in enumerate(data.items()):
        first_dates = level_data['first_attested']
        print(first_dates)

        x = []
        for j, (first_date_, last_date_) in enumerate(
                zip(level_data['first_attested'], level_data['last_attested'])
        ):
            if last_date_ is NO_DATE and first_date_ is NO_DATE:
                continue

            _x = (last_date_ - first_date_).total_seconds() * 1000
            print(_x)
            # x.append((last_date_ - first_date_).total_seconds() * 1000)

            print(first_date_, last_date_)

            fig.add_bar(**{
                'alignmentgroup': 'True',
                'base': array(first_date_, dtype=object),
                # 'base': array(first_date_, ),
                # 'customdata': level,
                'name': level,
                'hovertemplate': (
                    'level=%{name}<br>'
                    'first_attested=%{base}<br>'
                    'last_attested=%{x}<br>'
                    'construction_id=%{y}'
                    '<extra></extra>'
                ),
                # 'text': (
                #     f'{first_date_}-{last_date_}'
                # ),
                'legendgroup': level,
                'marker': {'color': COLORS[level], 'opacity': 0.6},
                'offset': 0.0 + {0: -1, 1: 1}[i] * 0.03 + j * 0.01,
                'width': 0.01,
                'offsetgroup': level,
                'orientation': 'h',
                'showlegend': True,
                'textposition': 'auto',
                # 'x': array(x),
                'x': array(_x),
                'xaxis': 'x',
                # 'y': array([1, 1, 1, 1], dtype='int64'),
                'y': array(1),
                'yaxis': 'y'
            })

    graphJSON = str(fig.to_json())

    return graphJSON


def plot_single_const_changes(
        df: pd.DataFrame,
        no_last_date_option: Literal['current' or 'largest'] = 'largest'
):
    fig = go.Figure(
        layout={
            'barmode': 'overlay',
            'legend': {'title': {'text': 'level'}, 'tracegroupgap': 0},
            'margin': {'t': 60},
            # 'template': '...',
            'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0], 'type': 'date', 'title': {'text': 'year'}},
            'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0], }  # 'title': {'text': 'construction_id'}}
        }
    )

    fig.add_bar(**{
        'alignmentgroup': 'True',
        'base': array(['1850', '1831', '1857', '1873'], dtype=object),
        'hovertemplate': ('level=%{name}<br>first_attested=%{base}<br>'
                          'last_attested=%{x}<br>construction_id=%{y}'
                          '<extra></extra>'),
        'legendgroup': 'synt',
        'marker': {'color': '#636efa', 'opacity': 0.6},
        'name': 'synt',
        'offset': 0.0,
        'width': 0.1,
        'offsetgroup': 'synt',
        'orientation': 'h',
        'showlegend': True,
        'textposition': 'auto',
        'x': array([1.1360736e+12, 4.8282048e+12, 3.1553280e+11, 4.4810496e+12]),
        'xaxis': 'x',
        'y': array([1, 1, 1, 1], dtype='int64'),
        'yaxis': 'y'
    })

    fig.add_bar(**{
        'alignmentgroup': 'True',
        'base': array(['1850', '1831'], dtype=object),
        'hovertemplate': ('level=%{name}<br>first_attested=%{base}<br>'
                          'last_attested=%{x}<br>construction_id=%{y}'
                          '<extra></extra>'),
        'legendgroup': 'sem',
        'marker': {'color': '#EF553B', 'opacity': 0.6},
        'name': 'sem',
        'offset': -0.1,
        'width': 0.1,
        'offsetgroup': 'sem',
        'orientation': 'h',
        'showlegend': True,
        'textposition': 'auto',
        'x': array([1.1360736e+12, 3.1561920e+11]),
        'xaxis': 'x',
        'y': array([1, 1], dtype='int64'),
        'yaxis': 'y'
    })

    # fig = px.timeline(
    #     df, x_start="first_attested", x_end="last_attested",
    #     y="construction_id", color='level',
    #     opacity=.6,
    #                   # , hover_name="hoverName"
    #                   # # , color_discrete_sequence=px.colors.qualitative.Prism
    #                   # , opacity=.6
    #                   # , template='plotly_white'
    #                   # , color='level'
    #                   # , hover_data=['first_attested', 'last_attested']
    # )

    # print(vars(fig))
    # print(fig.data)

    # print(list(fig.data))
    # for obj in fig.data:
    #     # stage, level = obj.hovertext[0].split("|")
    #     # print(stage, level)
    #     print(obj)
    #     level = obj.name
    #     if (level == 'synt'):
    #         obj.width = 0.1
    #         obj.offset = 0.0
    #     elif (level == 'sem'):
    #         obj.width = 0.1
    #         obj.offset = -0.1
    #     print(obj)
    #     print(obj.hovertemplate)
    #
    # fig.add_bar(**{
    #     'alignmentgroup': 'True',
    #     'base': array([1850, 1831], dtype=object),
    #     'hovertemplate': ('<b>%{hovertext}</b><br>'),
    #     'hovertext': array(['3|sem', '0|sem'], dtype=object),
    #     'legendgroup': 'sem2',
    #     'marker': {'color': '#EF553B', 'opacity': 0.6},
    #     'name': 'sem2',
    #     'offsetgroup': 'sem2',
    #     'orientation': 'h',
    #     'showlegend': True,
    #     'textposition': 'auto',
    #     'x': array([1860, 2015]),
    #     'xaxis': 'x',
    #     'y': array([3, 3], dtype=object),
    #     'yaxis': 'y'
    # })

    # data = [dict(Task="Job A", Start='2007', Finish='2010'),
    #         dict(Task="Job A", Start='2008', Finish='2010'),
    #         dict(Task="Job B", Start='2004', Finish='2010'),
    #         dict(Task="Job C", Start='2009', Finish='2010')]
    #
    # df = pd.DataFrame(data)
    #
    # df['JobNum'] = ""
    # df.loc[0, 'JobNum'] = 1
    # for idx in range(1, df.shape[0]):
    #     if df.loc[idx - 1, 'Task'] == df.loc[idx, 'Task']:
    #         df.loc[idx, 'JobNum'] = df.loc[idx - 1, 'JobNum'] + 1
    #     else:
    #         df.loc[idx, 'JobNum'] = 1
    #
    # df['hoverName'] = df.apply(lambda x: x['Task'] + "|" + str(x['JobNum']), axis=1)
    #
    # print(df.info())
    # print(df['Start'])
    # print(df['Finish'])

    # fig = px.timeline(df
    #                   , x_start="Start"
    #                   , x_end="Finish"
    #                   , y="Task"
    #                   , hover_name="hoverName"
    #                   # , color_discrete_sequence=px.colors.qualitative.Prism
    #                   , opacity=.7
    #                   , template='plotly_white'
    #                   , color='JobNum'
    #                   , hover_data=['Start', 'Finish']
    #                   )
    #
    # for obj in fig.data:
    #     Task, JobNum = obj.hovertext[0].split("|")
    #     if (int(JobNum) == 1):
    #         obj.width = 0.1
    #         obj.offset = 0.05
    #     elif (int(JobNum) == 2):
    #         obj.width = 0.1
    #         obj.offset = -0.05

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON = str(fig.to_json())

    return graphJSON


def super_new_plot_single_const_changes(
        data: Dict[str, Dict[str, List[datetime]]],
        no_last_date_option: Literal['current', 'largest'] = 'largest'
):
    assert 1 <= len(data) <= 2 and ('synt' in data or 'sem' in data)

    # make a filler to be used instead of unmarked last-attested dates
    if no_last_date_option == 'largest':
        LAST_DATE = max(_date for level in data
                        for _date in data[level]['last_attested'])
    elif no_last_date_option == 'current':
        LAST_DATE = datetime(datetime.now().year, 1, 1)
    else:
        raise ValueError

    for level, level_data in data.items():
        last_dates = level_data['last_attested']
        first_dates = level_data['first_attested']

        corrected_last_dates = []

        for i, last_date_ in enumerate(last_dates):
            if last_date_ is NO_DATE and first_dates[i] is NO_DATE:
                # remove first_date and don't add last_date
                first_dates.pop(i)
                continue
            elif last_date_ is NO_DATE:
                last_date_ = LAST_DATE

            corrected_last_dates.append(last_date_)

        data[level]['last_attested'] = corrected_last_dates

    print(LAST_DATE, data, last_dates, corrected_last_dates, sep='\n')

    fig = go.Figure(
        layout={
            'barmode': 'overlay',
            'legend': {'title': {'text': 'level'}, 'tracegroupgap': 0},
            'margin': {'t': 60},
            # 'template': '...',
            'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0], 'type': 'date', 'title': {'text': 'year'}},
            'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0], }  # 'title': {'text': 'construction_id'}}
        }
    )

    get_dates = itemgetter('first_attested', 'last_attested')
    for i, (level, level_data) in enumerate(data.items()):

        x = []
        suiting_dates = (date for date in zip(*get_dates(level_data))
                         if not date[0] is NO_DATE or date[1] is NO_DATE)

        print(level_data, list(suiting_dates))

        for first_date_, last_date_ in suiting_dates:
            x.append((last_date_ - first_date_).total_seconds() * 1000)

            fig.add_traces([go.Scatter(**{
                # 'alignmentgroup': 'True',
                # 'base': array(first_dates, dtype=object),
                # 'customdata': level,
                'hovertemplate': (
                    'level=%{name}<br>first_attested=%{base}<br>'
                    'last_attested=%{x}<br>construction_id=%{y}'
                    '<extra></extra>'
                ),
                'legendgroup': level,
                'marker': {'color': COLORS[level], 'opacity': 0.6},
                'name': level,
                # 'offset': 0.0 - i * 0.05,
                # 'width': 0.05,
                'offsetgroup': level,
                'orientation': 'h',
                'showlegend': True,
                # 'textposition': 'auto',
                'x': [first_date_, last_date_],
                'xaxis': 'x',
                'y': [1, 1],
                # 'y': array([1, 1, 1, 1], dtype='int64'),
                'yaxis': 'y'
            })])

    graphJSON = str(fig.to_json())

    return graphJSON




