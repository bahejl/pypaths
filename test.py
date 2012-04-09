import unittest

import pypath


'''
p1.cmppath(p2)
cmppath(p1, p2)
'''

class TestPath(unittest.TestCase):
    def setUp(self):
        pass

    def test_cmppath(self):
        '''


        p1 = 'TCPIP Demo App'
        p2 = 'TCPIP\\Demo App'
        p3 = 'Demo App'
        assertTrue(cmppath(p1, p2) > max(cmppath(p1, p3), cmppath(p2, p3))

        p1 = "Node 1/Precompiled HEX/8bit Wireless Kit" 
        p2 = "Node 1/Precompiled HEX/8bit WDK"
        p3 = "Node 2/Precompiled HEX/8bit WDK"
        assertTrue(cmppath(p1, p2) > cmppath(p1, p3))
        '''
        pass

    def test_cmpchildren(self):
        '''

        '''
        pass

    def test_bestmatch(self):
        '''
        ensure that best match is selected if max

        p1 = 'TCPIP Demo App'
        p2 = 'TCPIP\\Demo App'
        p3 = 'Demo App'
        assertEqual(bestmatch(p1, (p2, p3)), p2)

        p1 = "Node 1/Precompiled HEX/8bit Wireless Kit" 
        p2 = "Node 1/Precompiled HEX/8bit WDK"
        p3 = "Node 2/Precompiled HEX/8bit WDK"
        assertEqual(bestmatch(p1, (p2, p3)), p2)

        p1 = "USB Device - Bootloaders"
        p2 = "USB\Device - Bootloaders"
        p3 = "USB\Device - Bootloaders\HID\Firmware - PIC18 Non-J\Linker files for applications"
        assertEqual(bestmatch(p1, (p2, p3), p2)

        '''
        pass


if __name__ == '__main__':
    unittest.main()
