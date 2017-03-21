import sys


class BaseTest(object):
    subtest_str = None

    def run(self, debug=False):
        print('Test class: %s' % type(self).__name__)

        total_failed_count = 0
        total_success_count = 0

        for f in self.get_tests():
            print('Running test: %s... ' % f.__name__, end='')
            sys.stdout.flush()

            self.subtest_str = None

            success_count, failed_count = f(debug=debug)

            total_success_count += success_count
            total_failed_count += failed_count

            if failed_count == 0:
                print('OK!')
            else:
                print('FAILED!')

        print('%i/%i tests completed successfully' % (total_success_count, total_success_count + total_failed_count))
        if total_failed_count > 0:
            print('%i tests FAILED' % total_failed_count)

    def get_tests(self):
        return []

    def print_number(self, current, total):
        if self.subtest_str is not None:
            print(('\b' * len(self.subtest_str)), end='')

        self.subtest_str = '%i/%i ' % (current, total)

        print(self.subtest_str, end='')
        sys.stdout.flush()
