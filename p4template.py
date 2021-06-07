
MAX_BITS = 512 # Size of the field that P4 can handle

start = '''
/* -*- P4_16 -*- */

#include <core.p4>
#include <v1model.p4>

/*
 * Define the headers the program will recognize
 */

/*
 * Standard ethernet header 
 */
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

/*
 * This is a custom protocol header for the calculator. We'll use 
 * ethertype 0x1234 for is (see parser)
 */
const bit<16> P4CALC_ETYPE = 0x1234;

header tcamlookup_t {
    bit<''' + str(MAX_BITS) + '''> key;
}

/*
 * All headers, used in the program needs to be assembed into a single struct.
 * We only need to declare the type, but there is no need to instantiate it,
 * because it is done "by the architecture", i.e. outside of P4 functions
 */
struct headers {
    ethernet_t   ethernet;
    tcamlookup_t   tcamlookup;
}

/*
 * All metadata, globally used in the program, also  needs to be assembed 
 * into a single struct. As in the case of the headers, we only need to 
 * declare the type, but there is no need to instantiate it,
 * because it is done "by the architecture", i.e. outside of P4 functions
 */
 
struct metadata {
    /* In our case it is empty */
}

/*************************************************************************
 ***********************  P A R S E R  ***********************************
 *************************************************************************/
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            P4CALC_ETYPE : parse_tcamlookup;
            default      : accept;
        }
    }

    state parse_tcamlookup {
	packet.extract(hdr.tcamlookup);
	transition accept;
    }
}

/*************************************************************************
 ************   C H E C K S U M    V E R I F I C A T I O N   *************
 *************************************************************************/
control MyVerifyChecksum(inout headers hdr,
                         inout metadata meta) {
    apply { }
}

/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    
    action send_back(bit<''' + str(MAX_BITS) + '''> result) {
        bit<48> tmp;

        /* Put the result back in */
        hdr.tcamlookup.key = result;
        
        /* Swap the MAC addresses */
        tmp = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = tmp;
        
        /* Send the packet back to the port it came from */
        standard_metadata.egress_spec = standard_metadata.ingress_port;
    }
    

    action operation_incl() {
	send_back(1);
    }

    action operation_excl() {
	send_back(0);
    }

    action operation_drop() {
        mark_to_drop(standard_metadata);
    }
    
    table calculate {
        key = {
            hdr.tcamlookup.key        : ternary;
        }
        actions = {
            operation_excl;
	    send_back;
        }
        const default_action = operation_excl();
        const entries = {'''

end = '''
        }
    }

            
    apply {
        if (hdr.tcamlookup.isValid()) {
            calculate.apply();
        } else {
            operation_excl();
        }
    }
}

/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/
control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}

/*************************************************************************
 *************   C H E C K S U M    C O M P U T A T I O N   **************
 *************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
 ***********************  D E P A R S E R  *******************************
 *************************************************************************/
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.tcamlookup);
    }
}

/*************************************************************************
 ***********************  S W I T T C H **********************************
 *************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;'''
