from PyInquirer import prompt


def cli_command(network):
    choices = [
            {
                'name': 'Create an Equipment',
                'value': 'create equipment'
            },
            {
                'name': 'Show the network',
                'value': 'show network'
            },
            {
                'name': 'End',
                'value': 'end'
            }
    ]
    if len(network) != 0:
        choices.insert(
            -1,
            {
                'name': 'Show equipement detail',
                'value': 'show detail'
            },
        )
    if len(network) > 1:
        choices.insert(
            -1,
            {
                'name': 'Insert an equipement',
                'value': 'insert equipment'
            },
        )

    questions = [
        {
            'type': 'list',
            'name': 'command',
            'message': 'What do you want to do?',
            'choices': choices
        }
    ]
    answers = prompt(questions)
    return answers['command']


def cli_create_equipment():
    questions = [
        {
            'type': 'input',
            'name': 'id',
            'message': 'ID of the new equipment?'
        },
        {
            'type': 'input',
            'name': 'port',
            'message': 'port of the new equipment?'
        },
    ]
    answers = prompt(questions)
    equipment_id, port = answers['id'], int(answers['port'])
    return equipment_id, port


def cli_select_equipment(network, msg):
    choices = []
    for equipment in network:
        choices.append({
            'name': equipment.name,
            'value': equipment.name,
        })

    questions = [
        {
            'type': 'list',
            'name': 'selected_equipment_name',
            'message': msg,
            'choices': choices
        }
    ]
    answers = prompt(questions)

    for equipment in network:
        if equipment.name == answers['selected_equipment_name']:
            return equipment


def cli_validate(msg):
    questions = [
        {
            'type': 'confirm',
            'name': 'confirm',
            'message': msg
         },
        ]
    return prompt(questions)['confirm']
