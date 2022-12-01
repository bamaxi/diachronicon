from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Boolean,
    ForeignKey
)
from sqlalchemy import event
from sqlalchemy.orm import relationship

from app.database import (
    Base,
    db_session
)
from app.utils import read_lines


# SYNT_FUNCTION_OF_ANCHOR_VALUES = read_lines(
#     'app/database-meta/synt_function_of_anchor_values.txt'
# )

# these are known in advance and equal to RUssian Constructicon
SYNT_FUNCTION_OF_ANCHOR_VALUES = (
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

REPR_CHAR_LIM = 25


class GeneralInfo(Base):
    __tablename__ = 'general_info'

    construction_id = Column(Integer, ForeignKey("construction.id"),
                             primary_key=True)
    name = Column(String(200))

    # author data
    author_name = Column(String(50))
    author_surname = Column(String(50))
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


class Construction(Base):
    __tablename__ = 'construction'

    id = Column(Integer, primary_key=True)

    # TODO: do we want to search by parts of formula or anchors?
    #   if we do, and have a query language, with * or +, sql may not be enough
    #   postgreSQL with regex may work
    formula = Column(String(200))
    contemporary_meaning = Column(String(200))
    variation = Column(String(200))

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

    general_info = relationship("GeneralInfo", back_populates="construction",
                                uselist=False)  # One-to-one

    formula_elements = relationship(
        "FormulaElement", back_populates="construction",
        cascade="all, delete-orphan"  # TODO: check if setting is proper
    )

    changes = relationship(
        "Change", back_populates="construction",
        cascade="all, delete-orphan"  # TODO: check if setting is proper
    )

    # Uni-directional one-to-many
    constraints = relationship(
        "Constraint", order_by="Constraint.id"
    )

    def exist_constraints(self):
        return bool(self.constraints)

    def exist_changes_constraints(self):
        return any(change.exist_constraints() for change in self.changes)

    def __repr__(self):
        return (f'Construction({self.id!r}, {self.formula!r}, '
                f'{self.contemporary_meaning!r}, {self.variation!r}, '
                f'{self.in_rus_constructicon!r}, {self.rus_constructicon_id!r}, '
                f'{self.synt_function_of_anchor!r}, {self.anchor_schema!r}, '
                f'{self.anchor_ru!r}, {self.anchor_eng!r})')


class FormulaElement(Base):
    # TODO: implement tests
    __tablename__ = 'formula_element'

    id = Column(Integer, primary_key=True)
    construction_id = Column(Integer, ForeignKey(Construction.id))

    value = Column(String(100))
    order = Column(Integer)
    is_optional = Column(Boolean)
    has_variants = Column(Boolean, nullable=True)

    construction = relationship(
        "Construction", back_populates="formula_elements",
    )

    def __repr__(self):
        return (f'FormulaElement({self.id!r}, {self.value!r}, '
                f'{self.order!r}, {self.is_optional!r})')


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
    level = Column(String(10))
    type_of_change = Column(String(50))
    # TODO: datetime or int?
    first_attested = Column(Integer)
    last_attested = Column(Integer)

    first_example = Column(String(500))
    last_example = Column(String(500))

    comment = Column(String(700))

    construction = relationship(
        "Construction", back_populates="changes",
    )

    # Uni-directional one-to-many
    constraints = relationship(
        "Constraint",
        order_by="Constraint.id"
        # back_populates="change",
        # cascade="all, delete-orphan"  # TODO
    )

    def exist_constraints(self):
        return bool(self.constraints)

    def __repr__(self):
        return (f'Change({self.id!r}, {self.construction_id!r}, '
                f'{self.stage!r}, {self.level!r}, {self.type_of_change!r} '
                f'{self.first_attested!r}, {self.last_attested!r}, '
                f'{self.first_example!r:.{REPR_CHAR_LIM}}, '
                f'{self.last_example!r:.{REPR_CHAR_LIM}})')


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


