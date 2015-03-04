import logging
logger = logging.getLogger('compdb')

LEGAL_COMMANDS = ['init', 'config', 'snapshot', 'restore', 'cleanup', 'remove_project']

def store_snapshot(raw_args):
    from . import get_project
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        'snapshot',
        type = str,
        help = "Name of the file used to create the snapshot.",)
    parser.add_argument(
        '--database-only',
        action = 'store_true',
        help = "Create only a snapshot of the database, without a copy of the value storage.",)
    args = parser.parse_args(raw_args)
    project = get_project()
    try:
        if args.database_only:
            project.create_db_snapshot(args.snapshot)
        else:
            project.create_snapshot(args.snapshot)
    except Exception as error:
        print("Failed to create snapshot.")
        print(error)
    else:
        msg = "Successfully created snapshot '{sn}' of '{pr}'."
        print(msg.format(sn = args.snapshot, pr = project.get_id()))

def restore_snapshot(raw_args):
    from . import get_project
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        'snapshot',
        type = str,
        help = "Name of the snapshot file or directory, used for restoring.",
        )
    args = parser.parse_args(raw_args)
    project = get_project()
    project.restore_snapshot(args.snapshot)

def clean_up(raw_args):
    from . import get_project
    from . job import PULSE_PERIOD
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '-t', '--tolerance-time',
        type = int,
        help = "Tolerated time in seconds since last pulse before a job is declared dead.",
        default = int(5 * PULSE_PERIOD))
    args = parser.parse_args(raw_args)
    project = get_project()
    logger.info("Killing dead jobs...")
    project.kill_dead_jobs(seconds = args.tolerance_time)

def remove(raw_args):
    from argparse import ArgumentParser
    from . import get_project
    from . utility import query_yes_no
    project = get_project()
    question = "Are you sure you want to remove project '{}'?"
    if query_yes_no(question.format(project.get_id()), default = 'no'):
        try:
            project.remove()
        except RuntimeError as error:
            print("Error during project removal.")
            print("This can be caused by currently executed jobs.")
            print("Try 'compdb clenaup'.")
            if query_yes_no("Ignore this warning and remove anywas?", default = 'no'):
                project.remove(force = True)

def main():
    logging.basicConfig(level = logging.INFO)
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        'command',
        choices = LEGAL_COMMANDS,
        )

    args, more = parser.parse_known_args()

    if args.command == 'init':
        from compdb.contrib.init_project import main
        return main(more)
    elif args.command == 'config':
        from compdb.contrib.configure import main
        return main(more)
    elif args.command == 'snapshot':
        return store_snapshot(more)
    elif args.command == 'restore':
        return restore_snapshot(more)
    elif args.command == 'cleanup':
        return clean_up(more)
    elif args.command == 'remove_project':
        return remove(more)
    else:
        print("Unknown command '{}'.".format(args.command))
