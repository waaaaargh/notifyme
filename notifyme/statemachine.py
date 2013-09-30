# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes
# This file is part of notifyme.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class ProtocolState:
    """
    This is the Base class for a state machine. It's mainly there so that we
    don't have to write the constructor and it's documentation over and over
    again.

    """
    def __init__(self, context):
        """
        Initialize the state with a context it keeps and passes on to
        follownig states.

        Args:
            context(object): state of the machine and conection to the outside
                world.
        """
        self.context = context


class ReceivingProtocolState(ProtocolState):
    """
    This class exists only to make it clear semantically that this state is
    waiting for an incoming message.
    """
    pass


class SendingProtocolState(ProtocolState):
    """
    This class semantically defines that this state immediately sends out
    messages without waiting for messages to come in.
    """
    pass


class ProtocolStateMachine:
    """
    State Machine Implementation
    """
    def __init__(self, initial_state):
        """
        Initialize State Machine

        Args:
            initial_state(:class:`ProtocolState`): Initial State of the
                machine
        """
        self._state = initial_state

    def __call__(self, in_msg=None):
        """
        Advance to the next State, if any.

        Args:
            in_msg(:class:`notifyme.messages.ProtocolMessage`)
        """
        if isinstance(self._state, ReceivingProtocolState):
            self._state, out_msg = self._state(in_msg)
        elif isinstance(self._state, SendingProtocolState):
            self._state, out_msg = self._state()

        return out_msg

    @property
    def wait_for_input(self):
        """
        Check if we should wait for input

        Returns:
            Boolean
        """
        if isinstance(self._state, ReceivingProtocolState):
            return True
        elif isinstance(self._state, SendingProtocolState):
            return False
