class BaseTest(object):
    def run(self):
        print('Test class: %s' % type(self).__name__)

        total_failed_count = 0
        total_success_count = 0

        for f in self.get_tests():
            print('Running test: %s... ' % f.__name__, end='')

            success_count, failed_count = f()

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
