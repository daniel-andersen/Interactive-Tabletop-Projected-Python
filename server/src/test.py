import sys
from test.board_detection_test import BoardDetectionTest
from test.image_detection_test import ImageDetectionTest
from test.tiled_brick_detection_test import TiledBrickDetectionTest
from test.hand_detection_test import HandDetectionTest


# Tests to run
tests = [
    {'test': BoardDetectionTest(), 'filter': ['BOARD_DETECTION', 'ALL', 'BASIC']},
    {'test': TiledBrickDetectionTest(), 'filter': ['BRICK_DETECTION', 'ALL', 'BASIC']},
    {'test': HandDetectionTest(), 'filter': ['HAND_DETECTION', 'ALL', 'BASIC']},
    {'test': ImageDetectionTest(), 'filter': ['IMAGE_DETECTION', 'ALL', 'BASIC']},
]

# Parse arguments
args = sys.argv[1:]

filters = []

debug = False
for arg in args:
    if arg == '-d' or arg == '--debug':
        debug = True
    else:
        filters.append(arg)

if len(filters) == 0:
    filters = ['ALL']

# Run tests
total_success_count = 0
total_failed_count = 0

for test_dict in tests:

    # Filter check
    test_filter = test_dict['filter']

    should_run = False
    for f in filters:
        if f in test_filter:
            should_run = True

    if not should_run:
        continue

    # Run test
    test = test_dict['test']
    success_count, failed_count = test.run(debug=debug)

    total_success_count += 1 if failed_count == 0 else 0
    total_failed_count += 1 if failed_count > 0 else 0

print()
print('Result: %i/%i test%s completed successfully' % (total_success_count, total_success_count + total_failed_count, 's' if total_success_count > 1 else ''))
if total_failed_count > 0:
    print('        %i/%i test%s FAILED!' % (total_failed_count, total_success_count + total_failed_count, 's' if total_failed_count> 1 else ''))
print()
