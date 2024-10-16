import typing as T
from datetime import datetime
from itertools import chain
import logging

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Boolean,
    ForeignKey,
    Table,
)
from sqlalchemy import event
from sqlalchemy.orm import (
    relationship,
    declarative_base,
    declarative_mixin
)

from app.constants import NO_DATE


logger = logging.getLogger(f"diachronicon.{__name__}")
logger.addHandler(logging.StreamHandler())


PRECISE_DATE_UNTIL_YEAR = 2005
CURRENT_STATUS = "настоящее время"

MAX_FORMULA_LEN = 200
REPR_CHAR_LIM = 25


# these are known in advance and equal to Russian Constructicon
UNKNOWN_SYNT_FUNCTION_OF_ANCHOR = "<unknown>"
SYNT_FUNCTION_OF_ANCHOR_VALUES = (
    UNKNOWN_SYNT_FUNCTION_OF_ANCHOR,
    "Argument",
    "Coordinator",
    "Discourse Particle",
    "Government",
    "Matrix Predicate",
    "Modifier",
    "Nominal Quantifier",
    "Object",
    "Parenthetical",
    "Praedicative Expression",
    "Subject",
    "Subordinator",
    "Verb Predicate",
    "Word-Formation",
)


Base = declarative_base()

@declarative_mixin
class ShallowEqMixin:
    _comparable_args: T.List[str] = []

    def get_comparable_args(self):
        return self._comparable_args

    def __shallow_eq__(self, other: T.Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return all(getattr(self, _arg, None) == getattr(other, _arg, None)
                   for _arg in self._comparable_args)
    
    def shallow_eq(self, other: T.Any) -> bool:
        return self.__shallow_eq__(other)


class GeneralInfo(Base):
    __tablename__ = 'general_info'

    construction_id = Column(Integer, ForeignKey("construction.id"),
                             primary_key=True)
    name = Column(String(200))

    # project metadata
    supervisor = Column(String(60))

    # author data
    author_name = Column(String(60))
    author_surname = Column(String(60))
    group_number = Column(Integer)

    # links
    annotated_sample = Column(String(200))
    term_paper = Column(String(200))

    # TODO: this can be a binary `ready` field
    status = Column(String(30))

    construction = relationship("Construction", back_populates="general_info")

    def __repr__(self):
        return (f'GeneralInfo({self.construction_id!r}, {self.name!r}, {self.author_name!r}, '
                f'{self.author_surname!r}, {self.group_number!r}, '
                f'{self.annotated_sample!r}, {self.term_paper!r}, {self.status!r})')


@declarative_mixin
class TagMixin:
    id = Column(Integer, primary_key=True)
    name = Column(String(100))


SEMANTICS_TAG = "sem"
MORPHOSYNTAX_TAG = "synt"

class GeneralTag(TagMixin, Base):
    __tablename__ = "tag"
    kind = Column(Enum(
        *(SEMANTICS_TAG, MORPHOSYNTAX_TAG), name='tag_kind',
        create_constraint=True
    ))

    def __repr__(self):
        return (f'GeneralTag({self.id!r}, {self.name!r}, {self.kind!r})')


construction_to_tags = Table(
    "construction_to_tags",
    Base.metadata,
    Column("construction_id", Integer, ForeignKey("construction.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)

change_to_tags = Table(
    "change_to_tags",
    Base.metadata,
    Column("change_id", Integer, ForeignKey("change.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


@declarative_mixin
class ConstructionMixin:
    id = Column(Integer, primary_key=True)

    # TODO: do we want to search by parts of formula or anchors?
    #   if we do, and have a query language, with * or +, sql may not be enough
    #   postgreSQL with regex may work
    formula = Column(String(MAX_FORMULA_LEN))


class Construction(ConstructionMixin, Base):
    __tablename__ = 'construction'

    orig_id = Column(String(30))
    # id = Column(Integer, primary_key=True)
    #
    # # TODO: do we want to search by parts of formula or anchors?
    # #   if we do, and have a query language, with * or +, sql may not be enough
    # #   postgreSQL with regex may work
    # formula = Column(String(200))
    contemporary_meaning = Column(String(200))
    variation = Column(String(400))

    # TODO: the first is reducible to the latter (NULL => not in constructicon)
    in_rus_constructicon = Column(Boolean)
    rus_constructicon_id = Column(Integer)

    # synt_function_of_anchor = Column(String(30))
    synt_function_of_anchor = Column(
        Enum(*SYNT_FUNCTION_OF_ANCHOR_VALUES, name='synt_function_of_anchor',
             create_constraint=True)
        # String(100)
    )

    anchor_schema = Column(String(200))
    anchor_ru = Column(String(200))
    anchor_eng = Column(String(200))

    # TODO: normalize these into another table
    morphosyntags = Column(String(200))
    semantags = Column(String(200))
    morphosyntax_tags = relationship(
        "GeneralTag",
        secondary=construction_to_tags,
        # primaryjoin=id == construction_to_tags.c.construction_id,
        primaryjoin=f"and_(Construction.id==construction_to_tags.c.construction_id, GeneralTag.kind=='{MORPHOSYNTAX_TAG}')",
        # secondaryjoin=id == change_to_previous_changes.c.previous_change_id,
    )
    semantic_tags = relationship(
        "GeneralTag",
        secondary=construction_to_tags,
        # primaryjoin=id == construction_to_tags.c.construction_id,
        primaryjoin=f"and_(Construction.id==construction_to_tags.c.construction_id, GeneralTag.kind=='{SEMANTICS_TAG}')",
        # secondaryjoin=id == change_to_previous_changes.c.previous_change_id,
    )
    

    general_info = relationship("GeneralInfo", back_populates="construction",
                                uselist=False)  # One-to-one

    formula_elements = relationship(
        "FormulaElement", back_populates="construction",
        cascade="all, delete-orphan"  # TODO: check if setting is proper
    )

    changes = relationship(
        "Change", back_populates="construction",
        cascade="all, delete-orphan",  # TODO: check if setting is proper
        # order_by="Change.id"
    )

    # Uni-directional one-to-many
    constraints = relationship("Constraint", order_by="Constraint.id")

    variants = relationship(
        "ConstructionVariant", back_populates="construction",
        order_by="ConstructionVariant.id",
    )


    def get_alternate_formulas(self):
        return [variant.formula for variant in self.variants
                if variant.is_main != 1]

    def exist_constraints(self):
        return bool(self.constraints)

    def exist_changes_constraints(self):
        return any(change.exist_constraints() for change in self.changes)
    
    # @staticmethod
    # def _set_id1(lst: T.List['Change']):
    #     if not lst:
    #         return
    #     first_id = lst[0].id
    #     for item in lst:
    #         item.id1 = item.id - first_id + 1
    
    def set_changes_one_based(self):
        self.id_to_id1 = {}
        changes = self.changes
        if not changes:
            return changes
        
        for new_id1, ch in enumerate(changes, start=1):
            self.id_to_id1.setdefault(ch.id, new_id1)
            ch.id1 = new_id1
        
        for ch in changes:
            for _ch in chain(ch.previous_changes, ch.next_changes):
                _ch.id1 = self.id_to_id1[_ch.id]

        return changes

    def __repr__(self):
        return (f'Construction({self.id!r}, {self.formula!r}, '
                f'{self.contemporary_meaning!r}, {self.variation!r}, '
                f'{self.in_rus_constructicon!r}, {self.rus_constructicon_id!r}, '
                f'{self.synt_function_of_anchor!r}, {self.anchor_schema!r}, '
                f'{self.anchor_ru!r}, {self.anchor_eng!r}, '
                f'{self.morphosyntax_tags!r}, {self.semantic_tags!r})')


class ConstructionVariant(ConstructionMixin, Base):
    __tablename__ = 'construction_variant'

    construction_id = Column(Integer, ForeignKey(Construction.id))
    construction = relationship("Construction", back_populates="variants")
                                # uselist=False)  # One-to-one
    change_id = Column(Integer, ForeignKey("change.id"))

    changes = relationship("Change", back_populates="variants")
                            #  uselist=False)

    is_main = Column(Boolean)

    # formula = Column(String(200))

    formula_elements = relationship(
        "FormulaElement", back_populates="construction_variant",
        cascade="all, delete-orphan"  # TODO: check if setting is proper
    )

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.id!r}, {self.formula!r}, '
                f'{self.construction_id!r}, {self.construction!r}, '
                f'{self.is_main!r})')


class FormulaElement(Base, ShallowEqMixin):
    __tablename__ = 'formula_element'
    _comparable_args = ["value", "order", "depth", "is_optional", "has_variants"]

    id = Column(Integer, primary_key=True)
    formula_id = Column(Integer, unique=True)
    construction_id = Column(Integer, ForeignKey(Construction.id))
    construction_variant_id = Column(Integer, ForeignKey(ConstructionVariant.id))

    value = Column(String(100))
    order = Column(Integer)
    depth = Column(Integer)

    is_optional = Column(Boolean, default=False)
    has_variants = Column(Boolean, nullable=True)

    construction = relationship(
        "Construction", back_populates="formula_elements",
    )
    construction_variant = relationship(
        "ConstructionVariant", back_populates="formula_elements",
    )

    def __repr__(self):
        return (f'FormulaElement({self.id!r}, {self.value!r}, '
                f'{self.order!r}, {self.is_optional!r})')


# change_to_next_changes = Table(
#     "change_to_next_changes",
#     Base.metadata,
#     Column("change_id", Integer, ForeignKey("change.id"), primary_key=True),
#     Column("next_change_id", Integer, ForeignKey("change.id"), primary_key=True),
# )

change_to_previous_changes = Table(
    "change_to_previous_changes",
    Base.metadata,
    Column("change_id", Integer, ForeignKey("change.id"), primary_key=True),
    Column("previous_change_id", Integer, ForeignKey("change.id"), primary_key=True),
)


class Change(Base):
    __tablename__ = 'change'
    _names = {

        'стадия': 'stage',
        'уровень': 'level',
        'тип изменения': 'type_of_change',
        'первое вхождение (дата)': 'first_attested',
        'последнее вхождение (дата)': 'last_attested',
        'первое вхождение': 'first_example',
        'последнее вхождение': 'last_example',
        'комментарий': 'comment'
    }

    id = Column(Integer, primary_key=True)
    construction_id = Column(Integer, ForeignKey(Construction.id))

    # TODO: see in Construction, do we want to search by parts of stage?
    stage = Column(String(200))
    former_change = Column(String(50))

    level = Column(String(10))
    type_of_change = Column(String(50))
    subtype_of_change = Column(String(100))

    # TODO: normalize these into another table with Construction tags
    morphosyntags = Column(String(200))
    semantags = Column(String(200))
    morphosyntax_tags = relationship(
        "GeneralTag",
        secondary=change_to_tags,
        primaryjoin=f"and_(Change.id==change_to_tags.c.change_id, GeneralTag.kind=='{MORPHOSYNTAX_TAG}')",
    )
    semantic_tags = relationship(
        "GeneralTag",
        secondary=change_to_tags,
        primaryjoin=f"and_(Change.id==change_to_tags.c.change_id, GeneralTag.kind=='{SEMANTICS_TAG}')",
    )


    # TODO: datetime or int?
    first_attested = Column(Integer)
    last_attested = Column(Integer)

    first_example = Column(String(500))
    last_example = Column(String(500))

    # textual comments
    comment = Column(String(500))
    frequency_trend = Column(String(400))
    sources = Column(String(500))

    construction = relationship(
        "Construction", back_populates="changes",
    )

    variants = relationship(
        "ConstructionVariant", back_populates="changes",
        order_by="ConstructionVariant.id",
    )

    # Uni-directional one-to-many
    constraints = relationship(
        "Constraint",
        order_by="Constraint.id"
        # back_populates="change",
        # cascade="all, delete-orphan"  # TODO
    )

    previous_changes = relationship(
        "Change",
        secondary=change_to_previous_changes,
        primaryjoin=id == change_to_previous_changes.c.change_id,
        secondaryjoin=id == change_to_previous_changes.c.previous_change_id,
        # backref="next_changes",
        back_populates="next_changes"
    )

    next_changes = relationship(
        "Change",
        secondary=change_to_previous_changes,
        primaryjoin=id == change_to_previous_changes.c.previous_change_id,
        secondaryjoin=id ==  change_to_previous_changes.c.change_id,
        # backref="next_changes",
        back_populates="previous_changes"
    )

    @staticmethod
    def parse_year(year: T.Union[str, int, None], left_bias=0.0) -> T.Optional[int]:
        """Parse year string into datetime

        :param year:
        :param left_bias:
        :return:
        """
        if not year or year == '-':
            return None
        if isinstance(year, int) or year.isnumeric():
            return year
        if '-' in year:
            if year.endswith('-ые'):
                return int(year.split('-')[0])

            left, right = [int(part) for part in year.split('-')]
            return int(left + (right-left) * (1-left_bias))

        logger.debug(f"unsupported year type: `{year}`")
        return None

    
    @property
    def first_attested_(self) -> T.Union[int, str]:
        return self.parse_year(self.first_attested) or self.first_attested

    @property
    def last_attested_(self) -> T.Union[int, str]:
        return self.parse_year(self.last_attested) or self.last_attested

    
    @property
    def last_attested_dt_aware(self) -> T.Union[int, str]:
        year = self.parse_year(self.last_attested) or self.last_attested
        if isinstance(year, int):
            return year if year < PRECISE_DATE_UNTIL_YEAR else CURRENT_STATUS
            

    def exist_constraints(self):
        return bool(self.constraints)

    def dates_to_dict(self):
        dates = {}

        for field in ('first_attested', 'last_attested'):
            year = parse_year(getattr(self, field))
            value = datetime(year, 1, 1) if year else NO_DATE

            # dates.setdefault(field, []).append(value)
            dates[field] = value

    def __repr__(self):
        return (f'Change({self.id!r}, {self.construction_id!r}, '
                f'{self.stage!r}, {self.level!r}, {self.type_of_change!r} '
                f'{self.first_attested!r}, {self.last_attested!r}, '
                f'{self.first_example!r:.{REPR_CHAR_LIM}}, '
                f'{self.last_example!r:.{REPR_CHAR_LIM}}, '
                f'{self.morphosyntax_tags!r}, {self.semantic_tags!r})')


class Constraint(Base):
    __tablename__ = 'constraint'
    id = Column(Integer, primary_key=True)
    # TODO: make a better scheme? make both nullable?
    # null in case constraint is related to construction as a whole
    change_id = Column(Integer, ForeignKey(Change.id), nullable=True)
    construction_id = Column(Integer, ForeignKey(Construction.id))

    element = Column(String(30))
    syntactic = Column(String(300))
    semantic = Column(String(300))

    change = relationship(
        "Change", back_populates="constraints",
    )

    def __repr__(self):
        return (f'Constraint({self.id!r}, {self.change_id!r}, '
                f'{self.construction_id!r}, {self.element!r}, '
                f'{self.syntactic!r:.{REPR_CHAR_LIM}}, '
                f'{self.semantic!r:.{REPR_CHAR_LIM}})')


# @event.listens_for(Constraint, 'after_insert')
# def flag_constraints_existence(mapper, connection, target):
#     construction_id, change_id = Constraint.construction_id, Constraint.change_id
#
#     if change_id:
#         db_session.execute(select())

@event.listens_for(Construction.changes, "append")
def add_1based_id(target, value, initiator):
    print("append event on `Construction.changes`")
    print(target)
    print(value)
    print(initiator)


# @event.listens_for(Change.next_changes, "append")
# def add_1based_id(target, value, initiator):
#     print("append event on `Change.next_changes`")
#     print(target)
#     print(value)
#     print(initiator)

@event.listens_for(Change.previous_changes, "modified")
def add_1based_id(target, value, initiator):
    print("modified event on `Change.previous_changes`")
    print(target)
    print(value)
    print(initiator)


DBModel = T.Type[T.Union[
    Construction, Change, GeneralInfo, Constraint, FormulaElement,
    ConstructionVariant
]]
Model2Field2Val = T.Dict[DBModel, T.Union[T.Dict[str, T.Optional[str]],
                                      T.List[T.Dict[str, T.Optional[str]]]]]

