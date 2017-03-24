import sys


class BaseTest(object):
    current_test_output_string = None
    current_test_name = ''

    def run(self, debug=False):
        print('\nTest class: %s' % type(self).__name__)

        total_failed_count = 0
        total_success_count = 0

        for f in self.get_tests():
            self.current_test_name = f.__name__
            self.current_test_output_string = None

            success_count, failed_count = f(debug=debug)

            total_success_count += success_count
            total_failed_count += failed_count

        print('\n%i/%i test%s completed successfully' % (total_success_count, total_success_count + total_failed_count, 's' if total_success_count > 1 else ''), end='')
        if total_failed_count > 0:
            print('. %i test%s FAILED!' % (total_failed_count, 's' if total_failed_count > 1 else ''), end='')
        print()

        return total_success_count, total_failed_count

    def get_tests(self):
        return []

    def print_number(self, current, total):
        if self.current_test_output_string is not None:
            print(('\b' * len(self.current_test_output_string)), end='')

        self.current_test_output_string = 'Running test: %s... %i/%i ' % (self.current_test_name, current, total)

        print(self.current_test_output_string, end='')
        sys.stdout.flush()
