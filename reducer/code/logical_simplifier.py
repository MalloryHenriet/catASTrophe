import sqlparse
from sqlparse.sql import Where, IdentifierList, Identifier, TokenList
from sqlparse.tokens import Keyword, Whitespace, Punctuation, Wildcard

class LogicalSimplifier:
    def __init__(self, parser, validator):
        self.parser = parser
        self.validator = validator

    def simplify(self, tokens_list):
        simplified = []
        for tokens in tokens_list:
            stmt = self._simplify_where_clause(tokens)
            stmt = self._simplify_from_clause(stmt)
            stmt = self._simplify_select_clause(stmt)
            simplified.append(stmt)
        return simplified

    def _simplify_where_clause(self, stmt):
        original_sql = self.parser.to_sql([stmt])
        where_token = next((t for t in stmt.tokens if isinstance(t, Where)), None)
        if not where_token:
            return stmt

        comparisons = self._split_conditions(where_token)
        kept = comparisons[:]
        for cond in comparisons:
            trial = [c for c in kept if c != cond]
            new_where = self._join_conditions(trial)
            new_stmt = self._replace_clause(stmt, Where, new_where)
            simplified_sql = self.parser.to_sql([new_stmt])
            try:
                if self.validator(self.parser.parse(original_sql), self.parser.parse(simplified_sql)):
                    kept = trial
            except Exception:
                continue

        final_where = self._join_conditions(kept)
        return self._replace_clause(stmt, Where, final_where)

    def _split_conditions(self, where_token):
        parts = []
        current = []
        for token in where_token.tokens:
            if token.ttype is Keyword and token.value.upper() == 'AND':
                if current:
                    parts.append(current)
                    current = []
            elif token.ttype not in (Whitespace, Punctuation) or token.value not in ('(', ')'):
                current.append(token)
        if current:
            parts.append(current)
        return parts

    def _join_conditions(self, condition_tokens_list):
        all_tokens = []
        for idx, cond in enumerate(condition_tokens_list):
            if idx > 0:
                all_tokens.append(sqlparse.sql.Token(Whitespace, ' '))
                all_tokens.append(sqlparse.sql.Token(Keyword, 'AND'))
                all_tokens.append(sqlparse.sql.Token(Whitespace, ' '))
            all_tokens.extend(cond)
        return Where(all_tokens)

    def _simplify_from_clause(self, stmt):
        original_sql = self.parser.to_sql([stmt])
        for i, token in enumerate(stmt.tokens):
            if token.ttype is Keyword and token.value.upper() == 'FROM':
                next_token = stmt.tokens[i + 2] if stmt.tokens[i + 1].ttype is Whitespace else stmt.tokens[i + 1]
                if isinstance(next_token, IdentifierList):
                    sources = list(next_token.get_identifiers())
                elif isinstance(next_token, Identifier):
                    sources = [next_token]
                else:
                    return stmt

                kept = sources[:]
                for source in sources:
                    trial = [s for s in kept if s != source]
                    new_from = self._join_sources(trial)
                    new_tokens = stmt.tokens[:i+1] + [sqlparse.sql.Token(Whitespace, ' '), new_from] + stmt.tokens[i+2:]
                    new_stmt = TokenList(new_tokens)
                    simplified_sql = self.parser.to_sql([new_stmt])
                    try:
                        if self.validator(self.parser.parse(original_sql), self.parser.parse(simplified_sql)):
                            kept = trial
                    except Exception:
                        continue

                final_from = self._join_sources(kept)
                stmt.tokens = stmt.tokens[:i+1] + [sqlparse.sql.Token(Whitespace, ' '), final_from] + stmt.tokens[i+2:]
                return stmt
        return stmt

    def _simplify_select_clause(self, stmt):
        original_sql = self.parser.to_sql([stmt])
        select_seen = False

        for i, token in enumerate(stmt.tokens):
            if token.ttype is Keyword and token.value.upper() == 'SELECT':
                select_seen = True
                continue

            if select_seen:
                if isinstance(token, IdentifierList):
                    columns = list(token.get_identifiers())
                    kept = columns[:]
                    for col in columns:
                        trial = [c for c in kept if c != col]
                        new_select = self._join_sources(trial)
                        new_tokens = stmt.tokens[:i] + [new_select] + stmt.tokens[i+1:]
                        new_stmt = TokenList(new_tokens)
                        simplified_sql = self.parser.to_sql([new_stmt])
                        try:
                            if self.validator(self.parser.parse(original_sql), self.parser.parse(simplified_sql)):
                                kept = trial
                        except Exception:
                            continue

                    final_select = self._join_sources(kept)
                    stmt.tokens = stmt.tokens[:i] + [final_select] + stmt.tokens[i+1:]
                    return stmt

                elif isinstance(token, Identifier) or token.ttype is Wildcard:
                    # Only one column, cannot simplify further
                    return stmt
        return stmt

    def _join_sources(self, sources):
        all_tokens = []
        for idx, src in enumerate(sources):
            if idx > 0:
                all_tokens.append(sqlparse.sql.Token(Punctuation, ','))
                all_tokens.append(sqlparse.sql.Token(Whitespace, ' '))
            all_tokens.extend(src.tokens)
        return IdentifierList(all_tokens)

    def _replace_clause(self, stmt, clause_type, new_clause):
        new_tokens = []
        for token in stmt.tokens:
            if isinstance(token, clause_type):
                new_tokens.append(new_clause)
            else:
                new_tokens.append(token)
        return TokenList(new_tokens)
