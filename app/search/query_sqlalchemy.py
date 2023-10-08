import typing as T
from copy import deepcopy
import re

import sqlalchemy.sql.expression
from sqlalchemy import (
    select,
    inspect,
    func,
    or_,
    and_
)
from sqlalchemy.orm import (
    aliased,
    joinedload,
    selectinload,
    Load,
    load_only
)
import sqlalchemy

from app.models import (
    Construction,
    Change,
    GeneralInfo,
    Constraint,
    FormulaElement,
    ConstructionVariant,
)

from app.search.query import (
    _VT,
    BasicFormType,
    ElementDerivation,
    FormType,
    Operators,
    OperatorsStr,
    QueryMeta,
    BaseQuery,
    BaseQueryElement,
    SubForm,
    Comparison,
    BinaryConnective,
    Conjunction,
    ConjunctionCopies,
    ValueWithSignDerivation,
    form,
    deriv,
)


DBModel: T.TypeAlias = T.Type[T.Union[
    Construction, Change, GeneralInfo, Constraint, FormulaElement,
    ConstructionVariant
]]

INPUT_WILDCARDS = ["*"]
OUT_WILDCARD = "%"
input_wildcards_re = re.compile(r"|".join(re.escape(wc) for wc in INPUT_WILDCARDS))


MAPPING = {
    "construction": Construction,
    "changes": Change,
}

_change = {
    "formula": "stage",
}
MODEL2RENAMES = {
    "construction": {
        "meaning": "contemporary_meaning",
    },
    "change": _change,
    "changes": _change,
}


def tokenize_formula_query(query: str):
    return [
        input_wildcards_re.sub(OUT_WILDCARD, tok)
        for tok in query.split()
    ]


class SQLQueryMeta(QueryMeta):
    _was_registry_copied = False

    def __new__(
        __mcls: type[T.Self], name: str, bases: tuple[type, ...],
        namespace: dict[str, T.Any], **kwargs: T.Any
    ) -> T.Self:
        BASE_REGISTRY = __mcls.REGISTRY

        if not __mcls._was_registry_copied:
            __mcls.REGISTRY = dict(BASE_REGISTRY)
            __mcls._was_registry_copied = True

        allowed_base_classes = BASE_REGISTRY.values()
        allowed_base_classes_names = list(BASE_REGISTRY)

        cls_name = __mcls.__name__
        parent_cls_name = __mcls.__bases__[0].__name__
        maybe_prefix = cls_name.removesuffix(parent_cls_name)

        # print(name, bases, namespace)
        # print(parent_cls_name, allowed_base_classes_names)
        # print(cls_name, parent_cls_name, maybe_prefix)

        
        if not any(base_cls in allowed_base_classes for base_cls in bases):
            raise ValueError(
                f"classes with this metaclass ({cls_name}) must base one of "
                f"[{', '.join(allowed_base_classes_names)}]"
            )

        name_no_prefix = name.removeprefix(maybe_prefix)
        if (not name.startswith(maybe_prefix)):
            raise ValueError(
                f"classes with this metaclass ({cls_name}) must have name that "
                f"starts with `{maybe_prefix}`"
            )

        new_cls = super().__new__(__mcls, name, bases, namespace, **kwargs)
        new_cls.fields_queried = None

        # pop prefixed name from the registry copy and replace the non-prefixed class
        __mcls.REGISTRY.pop(name)
        __mcls.REGISTRY[name_no_prefix] = new_cls

        return new_cls


# class SQLConjunction(Conjunction, metaclass=SQLQueryMeta): ...

class SQLStringPattern(BaseQueryElement, metaclass=SQLQueryMeta):
    def __init__(self, param: str, value: str) -> None:
        super().__init__()
        self.param = param
        self.pattern = value

        self.fields_queried = [param]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.param!r}, {self.pattern!r})"

    def __str__(self) -> str:
        return f'str-pattern("{self.pattern}")'
    
    def __tree_repr__(self) -> str:
        return self.__str__()

    def query(self, stmt=None, model: T.Optional["SQLSubForm"]=None,
              query_model: T.Optional[BaseQuery] = None, **kwargs):
        return stmt.where(getattr(model, self.param).ilike(self.pattern))



def _make_skip_optional_subquery(cur_elem, distance, model=FormulaElement):
    return select(model.id).where(
        FormulaElement.construction_id == cur_elem.construction_id,
        FormulaElement.is_optional == True,
        cur_elem.order == FormulaElement.order + distance,
    )


# def make_byelem_formula_query(
#     stmt: sqlalchemy.sql.expression.Select,
#     model: T.Type[FormulaElement], value: str,
#     *args
# ):
#     """Update stmt to filter by formula elementwise, allowing simple regex/logic

#     :param stmt:
#     :param model:
#     :param value:
#     :return:
#     """
#     elements = value.split(' ')
#     print(elements)

#     element_tables = [aliased(FormulaElement) for i in range(len(elements))]

#     # params = {}

#     stmt = stmt.where(getattr(model, 'id') == element_tables[0].construction_id)

#     for i, (element_value, cur_elem_table) in enumerate(zip(elements, element_tables)):
#         # cur_elem_table = element_tables[i]

#         # TODO: опционально пропускать при поиске по элементам те, что в скобках
#         # TODO: asterisk instead of element
#         if i != 0:
#             stmt = stmt.where(
#                 cur_elem_table.construction_id == element_tables[0].construction_id,
#                 or_(
#                     cur_elem_table.order == element_tables[i-1].order + 1,
#                     and_(
#                         cur_elem_table.order == element_tables[i-1].order + 2,
#                         _make_skip_optional_subquery(cur_elem_table, 1).exists()
#                     )
#                 )
#             )

#         # params[f'gloss{i}'] = value  # or text(value)
#         corrected_val = element_value.replace('*', '%')
#         stmt = stmt.where(getattr(cur_elem_table, 'value').ilike(corrected_val))

#     return stmt

def format_kwargs(kwargs: T.Dict[str, T.Any], joiner=", ") -> str:
    return joiner.join([f"{name!r}={val!r}" for name, val in kwargs.items()])


def make_aliases(
        sql_model: DBModel, n: int,
        alias_adder: T.Optional[T.Callable[[DBModel], T.Any]]=None
    ) -> T.List[DBModel]:
    """Makes a list of `n` aliases with the model itself used in place of first alias
    
    This prevents `cartesian product` — proliferation of unneeded columns"""
    aliases = [aliased(sql_model) for i in range(n)]
    if alias_adder:
        for alias in aliases:
            alias_adder(alias)
    return [sql_model] + aliases


class SQLTokensQuery(BaseQueryElement, metaclass=SQLQueryMeta):
    def __init__(self, param: str, value: str, sql_model: DBModel=None, **kwargs) -> None:
        super().__init__()
        self.param = param
        self.value = value
        
        tokens = [SQLStringPattern("value", pat) for pat in self.tokenize(value)]
        self.tokens: T.List[T.Union[SQLStringPattern, SQLComparison]] = tokens

        self.fields_queried = [param]

        self.sql_model = sql_model
    
    def tokenize(self, query: str) -> T.List[str]:
        return tokenize_formula_query(query)
    
    def query(self, stmt, model: 'SQLSubForm', query_model: 'SQLQuery', **kwargs):
        tokens = self.tokens
        sql_model = self.sql_model or model.sql_model

        model_aliases = make_aliases(sql_model, len(tokens), query_model.add_sql_model)
        for i, (tok, aliased_model) in enumerate(zip(tokens, model_aliases)):
            if i != 0:
                stmt = stmt.where(
                    aliased_model.construction_id == model_aliases[0].construction_id,
                    or_(
                        aliased_model.order == model_aliases[i-1].order + 1,
                    )
                )

            stmt = tok.query(stmt, aliased_model)

        return stmt
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.param, self.value})"
    
    def __str__(self) -> str:
        return f'{self.param}={[f"{tok.__tree_repr__()}" for tok in self.tokens].__str__()}'

    def __tree_repr__(self) -> str:
        return self.__str__()


class SQLSubForm(SubForm, metaclass=SQLQueryMeta):
    def __init__(self, name: str, content: BaseQueryElement) -> None:
        if not name in MAPPING:
            raise ValueError(f"model unknown: {name}")
        
        super().__init__(name, content)

        self.fields_queried = content.fields_queried
        self.sql_model = MAPPING[name]

    def query(self, stmt = None, subform: T.Optional['SQLSubForm']=None, 
              query_model: T.Optional['SQLModel']=None, **kwargs):
        if stmt is None:
            raise ValueError(f"empty `stmt`")
        return self.content.query(stmt, self, query_model, **kwargs)


class SQLConjunction(Conjunction, metaclass=SQLQueryMeta):
    def __init__(self, items: T.List[BaseQueryElement]) -> None:
        super().__init__(items)

        self.fields_queried = sum([item.fields_queried for item in items], [])

    def query(self, stmt=None, subform: T.Optional[SQLSubForm]=None,
              query_model: T.Optional[BaseQuery]=None, **kwargs):
        for item in self.items:
            stmt = item.query(stmt, subform, query_model, **kwargs)

        return stmt
    

class SQLConjunctionCopies(ConjunctionCopies, metaclass=SQLQueryMeta):
    def __init__(self, items: T.List[BaseQueryElement]) -> None:
        super().__init__(items)

        self.fields_queried = sum([item.fields_queried for item in items], [])

    def query(self, stmt, subform: SQLSubForm, query_model: 'SQLQuery', **kwargs) -> T.Any:
        items = self.items

        # print(subform)

        model_aliases = make_aliases(subform.sql_model, len(items),
                                     query_model.add_sql_model)
        for alias in model_aliases:
            query_model.add_sql_model(alias)
        
        for item, alias in zip(items, model_aliases):
            subform.sql_model = alias
            stmt = item.query(stmt, subform, orig_model=subform.sql_model, **kwargs)

        return stmt


class SQLComparison(Comparison, metaclass=SQLQueryMeta):
    def __init__(self, param: str, op: OperatorsStr | Operators, value: _VT) -> None:
        super().__init__(param, op, value)

        self.fields_queried = [param]

    def query(self, stmt, subform: SQLSubForm, query_model: BaseQuery, **kwargs):
        print(self, '', subform, sep="\n")
        sql_entity = getattr(self, "sql_model", None) or subform.sql_model
        print(sql_entity)

        final_param = self.param
        # final_param = MODEL2RENAMES.get(subform.name, {}).get(param, param)
        try:
            return stmt.where(self.op(getattr(sql_entity, final_param), self.value))
        except AttributeError as e:
            print(f"skipping {self}")
            return stmt


class SQLNumChangesComparison(Comparison):
    def __init__(self, param: str, op: OperatorsStr | Operators, value: _VT) -> None:
        # TODO: special cases with <1, 0, -1 ... | <

        super().__init__(param, op, value)
        self.fields_queried = [param]

    def query(self, stmt, subform: SubForm, query_model: BaseQuery, **kwargs) -> T.Any:
        # assume Construction.id is always selected
        stmt = stmt.group_by(Construction.formula).having(
            self.op(func.count(Construction.changes), self.value)
        )
        return stmt
    
    def __str__(self) -> str:
        return f"count(construction.changes) {self.op2sign(self.op)} {self.value}"


class SQLDurationComparison(Comparison):
    def __init__(self, param: str, op: OperatorsStr | Operators, value: _VT) -> None:
        super().__init__(param, op, value)
        self.fields_queried = [param]

    def query(self, stmt, subform: SubForm, query_model: BaseQuery, **kwargs) -> T.Any:
        sql_model = subform.sql_model
        stmt = stmt.where(
            self.op((sql_model.last_attested - sql_model.first_attested), self.value) 
        )
        return stmt
    
    def __str__(self) -> str:
        return f"(last_attested - first_attested) {self.op2sign(self.op)} {self.value}"


class SQLQuery(BaseQuery, metaclass=SQLQueryMeta):
    def __init__(
        self, form2derivable_fields: T.Optional[T.Dict[str, T.List[ElementDerivation]]]=None
    ) -> None:
        super().__init__(form2derivable_fields)

        self.sql_models_queried: T.Set[DBModel] = set()
        self.sql_models_to_query: T.Set[DBModel] = set()

    def _make_construction_stmt(self):
        """Make statement considered basic — a construction statement """
        self.sql_models_queried |= {Construction, GeneralInfo}
        return select(
            Construction.id, Construction.formula, GeneralInfo.name
        ).join_from(Construction, GeneralInfo)
    
    def apply_join(self, stmt, maybe_left: DBModel, maybe_right: DBModel):
        print(f"attempting to join: {maybe_left} {maybe_right}")
        return stmt.join_from(maybe_left, maybe_right)

    def _make_base_statement(self):
        stmt = basic_stmt = self._make_construction_stmt()
        print(basic_stmt)

        # for subform in self.subforms_used:
        print("showing `sql_models_queried`:", self.sql_models_queried)
        all_models = [subform.sql_model for subform in self.subforms_used] + list(self.sql_models_to_query)
        print("all models", all_models, sep="\n")
        for sql_model in all_models: 
            if not sql_model in self.sql_models_queried:
                print(sql_model)
                stmt = self.apply_join(stmt, Construction, sql_model)
                self.sql_models_queried |= {sql_model}

        print("showing fields queried:")
        for subform in self.subforms_used:
            print(subform.fields_queried)

        return stmt
    
    def add_sql_model(self, model: DBModel):
        print(f"adding model: {model}")
        self.sql_models_to_query |= {model}

    def parse_val(self, form_name: str, key: str, val: str) -> BaseQueryElement:
        if form_name == "construction":
            if key == "formula":
                self.sql_models_to_query |= {FormulaElement}
                return SQLTokensQuery(key, val, sql_model=FormulaElement)
            # if key == "num_changes":
            #     self.add_sql_model(Change)
            #     return SQLNumChangesComparison(key, val)

        elif form_name == "change":
            if key == "stage":
                return SQLStringPattern(key, value)

        return super().parse_val(form_name, key, val)
    
    def derive_field(self, form: FormType | BasicFormType, form_name: str | None, field_derivation: ElementDerivation):
        maybe_derived_field = super().derive_field(form, form_name, field_derivation)

        print("derived a field:", maybe_derived_field)
        if isinstance(maybe_derived_field, SQLNumChangesComparison):
            self.add_sql_model(Change)

        return maybe_derived_field

    def check(
        self, subform: SQLSubForm, item: BaseQueryElement,
        parent_container: T.List[T.Any]
    ) -> bool:
        print(f"subform: {subform}\nitem:{item}\nparent_container:{parent_container}")

        if isinstance(item, BinaryConnective):
            additions = []
            removals = set()
            for i, _elem in enumerate(item.items):
                need_pop = self.check(subform, _elem, additions)
                if need_pop:
                    removals.add(i)
            
            print(f"binary connective item: {item}\nadditions: {additions}\nremovals: {removals}")

            item.items = [_elem for i, _elem in enumerate(item.items)
                          if i not in removals]
            item.items.extend(additions)

        elif isinstance(item, Comparison):
            print(f"comparison item: {item}")

            sql_model = subform.sql_model
            param = item.param
            if self.alt_comparison.get(sql_model, {}).get(param) is not None:
                args = {attr: getattr(item, attr) for attr in ("param", "op", "value")}
                new_item_model, callback = self.alt_comparison[sql_model][param]
                
                new_item = new_item_model(**args)
                if callback is not None:
                    callback(self)
                
                print(f"replacing comparison with: {new_item}")

                parent_container.append(new_item)
                
                return True
            
        elif isinstance(item, SubForm):
            self.check(item, item.content, None)

        else:
            raise ValueError(f"unexpected type: {type(item)}: {item}")

        return False

    def process_extra(self):
        self.check(None, self.form, None)
        print("check finished")


    def query(self, stmt=None, subform=None):
        if stmt is None:
            stmt = self._make_base_statement()
            print(f"form query: made base statement")
        
        return self.form.query(stmt, subform, self)
    

num_changes_deriv = ValueWithSignDerivation("num_changes", "num_changes_sign", SQLNumChangesComparison)
dur_deriv = ValueWithSignDerivation("duration", "duration_sign", SQLDurationComparison)
deriv = {"construction": [num_changes_deriv], "changes": [dur_deriv]}

def default_sqlquery():
    return SQLQuery(deriv)

# from pprint import pprint

# pprint(form)

# q = SQLQuery(deriv)
# res = q.parse_form(deepcopy(form), do_extra_processing=True)

# # pprint(res)

# print(res.__tree_repr__())

# final_stmt = q.query()
# print(final_stmt)
