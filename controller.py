from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.mac import haddr_to_bin
from ryu.lib import hub
import random
from operator import attrgetter

probe_byte_count = 0

class lbController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(lbController, self).__init__(*args, **kwargs)

        self.balance_thread = hub.spawn(self._balance)
        self.monitor_thread = hub.spawn(self._monitor)

        self.datapaths = {}
        self.path_data = {2:0, 3:0}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        self.datapaths[datapath.id] = datapath

    def _monitor(self):
        while True:
            if 1 in self.datapaths:
                datapath = self.datapaths[1]
                ofproto = datapath.ofproto
                parser = datapath.ofproto_parser

                req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
                datapath.send_msg(req)

            hub.sleep(2)

    def _request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(in_port=1)

        req = parser.OFPFlowStatsRequest(datapath, 0, ofproto.OFPTT_ALL,
                ofproto.OFPP_ANY, ofproto.OFPG_ANY, 1, 1, match)
        datapath.send_msg(req)

    def _add_balance_rule(self, dpid, mac, mac_mask, in_port, out_port):
        datapath = self.datapaths[dpid]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(in_port)
        match.set_dl_dst_masked(haddr, mask)
        actions = [parser.OFPActionOutput(out_port, 65535)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
            actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=100,
            match=match, instruction=inst) 

        datapath.send_msg(mod)

    def _balance(self):
        # IMMMD
        idx = 0;
        stats = [];
        haddr = None
        mask = None
        hub.sleep(1)
        global probe_byte_count

        while True:
            if idx == 0:
                # calculate solution set
                if (self.path_data[2] > self.path_data[3]):
                    balance_src = 2
                    balance_target = 3
                else:
                    balance_src = 3
                    balance_target = 2
                
                balance_amount = abs(self.path_data[2] - self.path_data[3])/2
    
                # algorithm (random trial)
                haddr, mask = self._add_random_trial_rule(balance_src)
                hub.sleep(1)
                
                idx = idx+1
                continue

            if idx == 1 or idx == 3:
                self._request_stats(self.datapaths[balance_src])
                idx = idx+1
                hub.sleep(1)
                continue

            if idx == 2 or idx == 4:
                stats.append(probe_byte_count)
                idx = idx+1
                hub.sleep(1)
                continue

            if idx == 5:
                # validate result
                bw = (stats[1] - stats[0])/2 * 8 / 1000
                
                if (balance_amount * 0.8 < bw < balance_amount * 1.2):
                    # found
                    self.logger.info("Found balance rules")
                    self._add_balance_rule(1, haddr, mask, 1, balance_target)
                    
                stats = []
                idx = 0
                hub.sleep(1)

    def _add_random_trial_rule(self, dpid):
        datapath = self.datapaths[dpid]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        bound_MAC = 5000
        bound_Mask = 4

        match = parser.OFPMatch(in_port=1)
        
        MAC= random.randint(bound_MAC, bound_MAC + 2**bound_Mask-1)
        haddr = "00:00:00:00:" + "{:02d}".format(MAC/100) + ":" + "{:02d}".format(MAC % 100)
        mask = "ff:ff:ff:ff:ff:f" + hex(0xf << random.randint(0, 4) & 0xf)[2:]

        self.logger.info("trying... mac: " + haddr + " mask: " + mask)

        haddr = haddr_to_bin(haddr)
        mask = haddr_to_bin(mask)
        match.set_dl_dst_masked(haddr, mask)

        actions = [parser.OFPActionOutput(2, 65535)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
            actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=100, cookie=1,
                cookie_mask=1, match=match, instructions=inst) 

        return haddr, mask

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        global probe_byte_count

        #for stat in sorted([flow for flow in body if flow.cookie == 1],
        #                   key=lambda flow: (flow.match['in_port'],
        #                                     flow.match['eth_dst'])):

        for stat in body:
            # print "cookie: " + str(stat.cookie)
            probe_byte_count = stat.byte_count
            print "got : " + str(probe_byte_count)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        for stat in sorted(body, key=attrgetter('port_no')):
            if stat.port_no != 2 and stat.port_no != 3:
                continue

            self.path_data.setdefault(stat.port_no, 0)
            self.logger.info('port %d bandwidth: %d Kbps', stat.port_no, (stat.tx_bytes - self.path_data[stat.port_no])*8/2/1000)
            self.path_data[stat.port_no] = stat.tx_bytes

