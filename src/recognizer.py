class Recognizer:
    def predict(self, rhs, dot, look_ahead, state_number, grammar, states):
        symbol_after_dot = rhs[dot]
        for rule in grammar.rules[symbol_after_dot]:
            if dot == len(rhs) - 1:
                new_state = (symbol_after_dot, rule, 0, look_ahead, state_number)
            else:
                lk_ahead = rhs[dot + 1]
                new_state = (symbol_after_dot, rule, 0, lk_ahead, state_number)

            if new_state not in states:
                states.append(new_state)

    def scan(self, state, state_number, tokens, state_sets):
        lhs, rhs, dot, look_ahead, origin = state
        dot += 1
        new_state = (lhs, rhs, dot, look_ahead, origin)

        next_state_set = state_number + 1
        if next_state_set == len(tokens):
            state_sets[(next_state_set, '')].append(new_state)
        else:
            state_sets[(next_state_set, tokens[next_state_set])].append(new_state)

    def complete(self, state_sets, states, state, tokens):
        lhs, rhs, dot, look_ahead, origin = state

        for old_state in state_sets[(origin, tokens[origin])]:
            old_lhs, old_rhs, old_dot, old_lkahead, old_origin = old_state

            if lhs == old_rhs[old_dot]:
                old_dot += 1
                new_state = (old_lhs, old_rhs, old_dot, old_lkahead, old_origin)
                if new_state not in states:
                    states.append(new_state)

    def parse(self, grammar, tokens, k=1):
        # add end marker to input string
        tokens.append('⊣')

        # create state sets corresponding to input tokens
        state_number = 0
        state_sets = {}
        for token in tokens:
            state_sets[(state_number, token)] = []
            state_number += 1
        state_sets[(state_number, '')] = []

        # add initial state to state 0
        lhs = 'Φ'
        rhs = [grammar.initial_nonterminal, '⊣']
        dot = 0
        look_ahead = '⊣'
        origin = 0

        state = (lhs, rhs, dot, look_ahead, origin)

        state_sets[(0, tokens[0])].append(state)

        # iterate through state sets in order
        for state_token, states in state_sets.items():
            state_number, token = state_token[0], state_token[1]

            for state in states:
                lhs, rhs, dot, look_ahead, origin = state
                if dot < len(rhs):
                    symbol_after_dot = rhs[dot]

                if dot == len(rhs) and state_number < len(tokens):
                    if token == look_ahead:
                        self.complete(state_sets, states, state, tokens)
                elif symbol_after_dot in grammar.nonterminals:
                    self.predict(rhs, dot, look_ahead, state_number, grammar, states)
                else:
                    if symbol_after_dot == token:
                        self.scan(state, state_number, tokens, state_sets)

        return state_sets
