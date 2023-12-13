import os
import json

# -------------------------------------------------------------------------------------------------------------------- #
#                                                         Load                                                         #
# -------------------------------------------------------------------------------------------------------------------- #


def load_rules(rules_name: str) -> dict:
    file = open(f"{os.getcwd()}/rules/{rules_name}.json", 'r')
    data: dict = json.loads(file.read())
    file.close()
    return data


def load_schema() -> list[dict]:
    file = open(f"{os.getcwd()}/temp/temp_schema.json", 'r')
    data: list[dict] = json.loads(file.read())
    file.close()
    return data

# -------------------------------------------------------------------------------------------------------------------- #
#                                                Conditions validations                                                #
# - Height
# - Width
# - Contains rivers
# - Has combinaisons
# - Combinaisons quantity is respected
# -------------------------------------------------------------------------------------------------------------------- #


def validate_height(schema: list[dict], rules: dict) -> bool:
    return all(x.get('height') == rules.get('height') for x in schema)


def validate_width(schema: list[dict], rules: dict) -> bool:
    isValid = True

    for x in schema:
        if not (x.get('width') == rules.get('width') or x.get('width') + 0.1 == rules.get('width')):
            isValid = False
        else:
            print(x.get('id'))

    return isValid

    # return all(x.get('width') == rules.get('width') or x.get('width') + 10 == rules.get('width') for x in schema)


def validate_rivers(schema: list[dict], rules: dict) -> bool:
    return True


def validate_combinaisons(schema: list[dict], rules: dict) -> bool:
    return True


def validate_combinaisons_quantity(schema: list[dict], rules: dict) -> bool:
    return True

# -------------------------------------------------------------------------------------------------------------------- #
#                                                        Result                                                        #
# -------------------------------------------------------------------------------------------------------------------- #


def validate_schema(rules_name) -> bool:
    schema = load_schema()
    rules = load_rules(rules_name)

    validate_width(schema, rules)

    # print(validate_width(schema, rules))

    return True

    # return validate_height(schema, rules) and \
    #     validate_width(schema, rules) and \
    #     validate_rivers(schema, rules) and \
    #     validate_combinaisons(schema, rules) and \
    #     validate_combinaisons_quantity(schema, rules)
