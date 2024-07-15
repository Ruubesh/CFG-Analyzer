class Recognizer:
    def create_state_sets(self, grammar, tokens):
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

        # final state
        final_state = (lhs, rhs, dot + 2, look_ahead, origin)

        state_sets[(0, tokens[0])].append(state)

        return state_sets, final_state

    def get_lookahead(self, look_ahead, rhs, dot, first_dict, grammar):
        lk_set = set()
        for index, symbol in enumerate(rhs[dot + 1:]):
            if symbol in grammar.nonterminals:
                first_set = first_dict[symbol]
                for terminal in first_set:
                    if terminal != 'epsilon':
                        lk_set.add(terminal)
                if 'epsilon' in first_set:
                    start_index = dot + 1
                    current_index = start_index + index
                    if current_index == len(rhs) - 1:
                        lk_set.add(look_ahead)
                else:
                    break
            else:
                lk_set.add(symbol)
                break

        return lk_set

    def predict(self, rhs, dot, look_ahead, state_number, grammar, states, first_dict):
        symbol_after_dot = rhs[dot]
        for rule in grammar.rules[symbol_after_dot]:
            if rule == ['']:
                rule = []

            if dot == len(rhs) - 1:
                new_state = (symbol_after_dot, rule, 0, look_ahead, state_number)

                if new_state not in states:
                    states.append(new_state)
            else:
                lk_set = self.get_lookahead(look_ahead, rhs, dot, first_dict, grammar)
                for lk_ahead in lk_set:
                    new_state = (symbol_after_dot, rule, 0, lk_ahead, state_number)

                    if new_state not in states:
                        states.append(new_state)

    def scan(self, states, state, state_number, tokens, state_sets, pointers_dict):
        lhs, rhs, dot, look_ahead, origin = state
        dot += 1
        new_state = (lhs, rhs, dot, look_ahead, origin)

        next_state_number = state_number + 1
        state_index = states.index(state)

        if next_state_number == len(tokens):
            next_states = state_sets[(next_state_number, '')]

            if (state_number, state_index) in pointers_dict:
                next_state_index = len(next_states)
                pointers = pointers_dict[(state_number, state_index)]
                pointers_dict[(next_state_number, next_state_index)] = pointers

            next_states.append(new_state)
        else:
            next_states = state_sets[(next_state_number, tokens[next_state_number])]

            if (state_number, state_index) in pointers_dict:
                next_state_index = len(next_states)
                pointers = pointers_dict[(state_number, state_index)]
                pointers_dict[(next_state_number, next_state_index)] = pointers

            next_states.append(new_state)

    def complete(self, state_number, state_sets, states, state, tokens, pointers_dict):
        lhs, rhs, dot, look_ahead, origin = state

        old_states = state_sets[(origin, tokens[origin])]
        for old_state in old_states:
            old_lhs, old_rhs, old_dot, old_lkahead, old_origin = old_state

            if old_dot == len(old_rhs):
                continue

            if lhs == old_rhs[old_dot]:
                old_dot += 1
                new_state = (old_lhs, old_rhs, old_dot, old_lkahead, old_origin)
                if new_state not in states:
                    old_state_index = old_states.index(old_state)
                    state_index = states.index(state)
                    new_state_index = len(states)

                    pointers = []
                    if (origin, old_state_index) in pointers_dict:
                        old_pointers = pointers_dict[(origin, old_state_index)]
                        pointers = old_pointers.copy()

                    pointers.append((state_number, state_index))

                    pointers_dict[(state_number, new_state_index)] = pointers

                    states.append(new_state)

    def parse(self, grammar, tokens, first_dict):
        # create state sets
        state_sets, final_state = self.create_state_sets(grammar, tokens)

        pointers_dict = {}

        # iterate through state sets in order
        for state_token, states in state_sets.items():
            state_number, token = state_token[0], state_token[1]

            if state_number == len(tokens):
                continue

            for state in states:
                lhs, rhs, dot, look_ahead, origin = state
                if dot < len(rhs):
                    symbol_after_dot = rhs[dot]

                if dot == len(rhs) and state_number < len(tokens):
                    if token == look_ahead:
                        self.complete(state_number, state_sets, states, state, tokens, pointers_dict)
                elif symbol_after_dot in grammar.nonterminals:
                    self.predict(rhs, dot, look_ahead, state_number, grammar, states, first_dict)
                else:
                    if symbol_after_dot == token:
                        self.scan(states, state, state_number, tokens, state_sets, pointers_dict)

        return state_sets, final_state, pointers_dict
