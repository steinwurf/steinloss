from steinloss.reorder import Reorder


class TestReorder:
    def test_iterate_through_window_twice_without_loss(self):
        reorder = Reorder()
        window_size = 5

        for n in range(0, window_size * 2):
            reorder.consume_packet(str(n))

        assert reorder.lost == 0

    def test_count_duplicates(self):
        reorder = Reorder()

        reorder.consume_packet('0')
        reorder.consume_packet('0')

        # lost package 1,2
        # package 3,4 is still in reordering window
        assert reorder.duplicate == 1

    def test_is_packet_loss_should_handle_reordering(self):
        reorder = Reorder()

        reorder.consume_packet('0')
        reorder.consume_packet('2')
        reorder.consume_packet('1')

        assert reorder.lost == 0

    def test_package_outside_reorder_window_do_not_get_counted(self):
        probe = Reorder()

        probe.consume_packet('0')
        probe.consume_packet('2')
        probe.consume_packet('3')
        probe.consume_packet('4')

        # not in reorder window
        probe.consume_packet('1')

        assert probe.lost == 1

    def test_count_loss_when_out_of_reorder_window(self):
        reorder = Reorder()

        reorder.consume_packet('0')
        reorder.consume_packet('4')

        # lost package 1,2
        # package 3,4 is still in reordering window
        assert reorder.lost == 1

    def test_count_old_reorder_window(self):
        reorder = Reorder()

        reorder.consume_packet('5')

        # lost package 0,1,2
        # package 3,4 is still in reordering window
        assert reorder.lost == 3

    def test_no_packet_loss_inside_window(self):
        probe = Reorder()

        probe.consume_packet('0')
        probe.consume_packet('2')
        probe.consume_packet('3')
        probe.consume_packet('1')

        assert probe.lost == 0

    def test_detect_loss(self):
        probe = Reorder()

        probe.consume_packet('1')
        probe.consume_packet('0')
        probe.consume_packet('2')
        probe.consume_packet('4')
        probe.consume_packet('5')
        probe.consume_packet('6')

        assert probe.lost == 1

    def test_count(self):
        probe = Reorder()

        probe.consume_packet('1')
        probe.consume_packet('4')

        assert probe.lost == 1

    def test_do_not_count_received_packages_in_reorder_window_as_loss(self):
        probe = Reorder()

        probe.consume_packet('0')
        probe.consume_packet('2')
        # 1 is lost
        probe.consume_packet('5')
        # 3,4 still in window

        assert probe.lost == 1

    def test_loss_between_packets(self):
        probe = Reorder()

        probe.consume_packet('0')
        probe.consume_packet('1')
        # missing 2
        probe.consume_packet('3')
        probe.consume_packet('4')
        # [3,4,2]
        # [1,1,0]
        probe.consume_packet('7')
        # får 7
        # new_lower_bound = 5
        # [6,7,5]
        # [0,1,0]

        assert probe.lost == 1
