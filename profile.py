#!/usr/bin/python

"""
Two SDR nodes running srsLTE software with SDR hardware. You may request
that it runs over the air, or within the controlled (PhantomNet) environment.

Specifically srsGUI and srsLTE code is pre-installed:

https://github.com/srsLTE/srsGUI

https://github.com/srsLTE/srsLTE

Instructions:

**To run the EPC**

Open a terminal on the epc-enb node in your experiment. (Go to the "List View"
in your experiment. If you have ssh keys and an ssh client working in your
setup you should be able to click on the black "ssh -p ..." command to get a
terminal. If ssh is not working in your setup, you can open a browser shell
by clicking on the Actions icon corresponding to the node and selecting Shell
from the dropdown menu.)

Start up the EPC:

    sudo srsepc
    
**To run the eNodeB**

Open another terminal on the epc-enb node in your experiment.

Start up the eNodeB:

    sudo srsenb

**To run the UE**

Open a terminal on the ue node in your experiment.

Start up the UE:

    sudo srsue

**Verify functionality**

Open another terminal on the ue node in your experiment.

Verify that the virtual network interface tun_srsue" has been created:

    ifconfig tun_srsue

Run ping to the SGi IP address via your RF link:
    
    ping 172.16.0.1

Killing/restarting the UE process will result in connectivity being interrupted/restored.

If you are using an ssh client with X11 set up, you can run the UE with the GUI
enabled to see a real time view of the signals received by the UE:

    sudo srsue --gui.enable 1


"""

import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.igext as ig
import geni.rspec.emulab.spectrum as spectrum


x310_node_disk_image = \
        "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"
b210_node_disk_image = \
        "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"

setup_command = "/local/repository/startup.sh"


def x310_node_pair(idx, x310_radio, node_type, installs):
    radio_link = request.Link("radio-link-%d"%(idx))
    radio_link.bandwidth = 10*1000*1000

    node = request.RawPC(x310_radio.node_name.format(
        radio_name=x310_radio.radio_name,
        idx=idx))
    node.hardware_type = node_type
    node.disk_image = x310_node_disk_image

    service_command = " ".join([setup_command] + installs)
    node.addService(rspec.Execute(shell="bash", command=service_command))

    node_radio_if = node.addInterface("usrp_if")
    node_radio_if.addAddress(rspec.IPv4Address("192.168.40.1",
                                               "255.255.255.0"))
    radio_link.addInterface(node_radio_if)

    radio = request.RawPC("x310-%d"%(idx))
    radio.component_id = x310_radio.radio_name
    radio_link.addNode(radio)


def b210_nuc_pair(idx, b210_node, installs):
    node_name = b210_node.node_name.format(idx=idx)
    b210_nuc_pair_node = request.RawPC(b210_node.node_name.format(
        idx=idx))
    b210_nuc_pair_node.component_manager_id = b210_node.aggregate_id
    b210_nuc_pair_node.component_id = b210_node.component_id

    b210_nuc_pair_node.disk_image = b210_node_disk_image

    service_command = " ".join([setup_command] + installs)
    b210_nuc_pair_node.addService(
        rspec.Execute(shell="bash", command=service_command))



portal.context.defineParameter("x310_pair_nodetype",
                               "Type of the node paired with the X310 Radios",
                               portal.ParameterType.STRING, "d740")

portal.context.defineStructParameter("x310_radios", "X310 Radios", [],
                                     multiValue=True,
                                     itemDefaultValue=
                                     {"node_name": "x310-node-{idx}"},
                                     min=0, max=None,
                                     members=[
                                         portal.Parameter(
                                             "radio_name",
                                             "Radio name, like cellsdr1-meb",
                                             portal.ParameterType.STRING,
                                             ""),
                                         portal.Parameter(
                                             "node_name",
                                             "Node name, will be .format'd "
                                             "with radio_name and idx",
                                             portal.ParameterType.STRING,
                                             "")
                                     ])

b210_agg_desc = """B210/NUC Aggregate|component id, e.g.:
'urn:publicid:IDN+law73.powderwireless.net+authority+cm|nuc2'"""
b210_agg_def = "urn:publicid:IDN+law73.powderwireless.net+authority+cm|nuc2"

fixed_endpoint_aggregates = [
    ("urn:publicid:IDN+web.powderwireless.net+authority+cm",
     "Warnock Engineering Building"),
    ("urn:publicid:IDN+ebc.powderwireless.net+authority+cm",
     "Eccles Broadcast Center"),
    ("urn:publicid:IDN+bookstore.powderwireless.net+authority+cm",
     "Bookstore"),
    ("urn:publicid:IDN+humanities.powderwireless.net+authority+cm",
     "Humanities"),
    ("urn:publicid:IDN+law73.powderwireless.net+authority+cm",
     "Law (building 73)"),
    ("urn:publicid:IDN+madsen.powderwireless.net+authority+cm",
     "Madsen Clinic"),
    ("urn:publicid:IDN+sagepoint.powderwireless.net+authority+cm",
     "Sage Point"),
    ("urn:publicid:IDN+moran.powderwireless.net+authority+cm",
     "Moran Eye Center"),
]


portal.context.defineStructParameter("b210_nodes", "Add Node", [],
                                     multiValue=True,
                                     itemDefaultValue=
                                     {"component_id": "nuc2",
                                      "node_name": "b210-node-{idx}"},
                                     min=0, max=None,
                                     members=[
                                         portal.Parameter(
                                             "component_id",
                                             "Component ID (like nuc2)",
                                             portal.ParameterType.STRING, ""),
                                         portal.Parameter(
                                             "aggregate_id",
                                             "Fixed Endpoint",
                                             portal.ParameterType.STRING,
                                             fixed_endpoint_aggregates[0],
                                             fixed_endpoint_aggregates),
                                         portal.Parameter(
                                             "node_name",
                                             "Node name, will be .format'd "
                                             "with idx",
                                             portal.ParameterType.STRING,
                                             "")
                                     ],
                                    )

portal.context.defineParameter("install_srslte",
                               "Should srsLTE Radio be installed?",
                               portal.ParameterType.BOOLEAN, True)
portal.context.defineParameter("install_gnuradio",
                               "Should GNU Radio (where uhd_fft, uhd_siggen, "
                               "etc) come from be installed?",
                               portal.ParameterType.BOOLEAN, True)
portal.context.defineParameter("install_gnuradio_companion",
                               "Should GNU Radio Companion be installed?",
                               portal.ParameterType.BOOLEAN, True)

channel_bandwidth_strings = [
    ('1.4', '1.4 MHz'),
    ('3', '3 MHz'),
    ('5', '5 MHz'),
    ('10', '10 MHz'),
    ('15', '15 MHz'),
    ('20', '20 MHz'),
]

# n PRB, width of frequency to allocate
channel_bandwidths = {
    '1.4': (6, 1.4, 0.5, 0.20),
    '3': (15, 3, 0.5, 0.20),
    '5': (25, 5, 0.5, 0.20),
    '10': (50, 10, 0.5, 0.20),
    '15': (75, 15, 0.5, 0.20),
    '20': (100, 20, 0.5, 0.20),
}

portal.context.defineStructParameter("frequency_config",
                                     "Channel Configuration for LTE",
                                     [{'downlink_frequency': 2685.0,
                                       'channel_bandwidth': '1.4'}],
                                     multiValue=True, min=0, max=1,
                                     members=[
                                         portal.Parameter(
                                             "downlink_frequency",
                                             "Downlink Frequency in MHz (will "
                                             "be rounded to nearest 100 kHz) "
                                             "must be in Band 7",
                                             portal.ParameterType.BANDWIDTH,
                                             2685.0),
                                         portal.Parameter(
                                             "channel_bandwidth",
                                             "Channel Bandwidth",
                                             portal.ParameterType.STRING,
                                             channel_bandwidth_strings[0],
                                             channel_bandwidth_strings),
                                     ],)

portal.context.defineStructParameter("frequency_ranges",
                                     "Extra Transmit Frequencies "
                                     "(other than LTE)", [],
                                     multiValue=True,
                                     itemDefaultValue=
                                     {},
                                     min=0, max=None,
                                     members=[
                                         portal.Parameter(
                                             "frequency_low",
                                             "Start frequency (MHz)",
                                             portal.ParameterType.BANDWIDTH,
                                             0.0),
                                         portal.Parameter(
                                             "frequency_high",
                                             "Stop frequency (MHz)",
                                             portal.ParameterType.BANDWIDTH,
                                             0.0)
                                     ])

params = portal.context.bindParameters()

request = portal.context.makeRequestRSpec()

installs = []

if len(params.frequency_config) > 0:
    downlink_frequency = params.frequency_config[0].downlink_frequency
    downlink_earfcn = downlink_frequency

    centi_khz = downlink_frequency * 10
    centi_khz = int(round(centi_khz))

    if centi_khz < 26200:
        raise Exception("Too low of a downlink frequency for band 7")
    if centi_khz > 26899:
        raise Exception("Too high of a downlink frequency for band 7")

    earfcn = centi_khz - 26200 + 2750

    channel_bandwidth_str = params.frequency_config[0].channel_bandwidth
    n_prb, bandwidth, ul_amp, dl_gain = \
            channel_bandwidths[channel_bandwidth_str]

    low_downlink_frequency = downlink_frequency - bandwidth/2
    high_downlink_frequency = downlink_frequency + bandwidth/2
    low_uplink_frequency = downlink_frequency - bandwidth/2 - 120
    high_uplink_frequency = downlink_frequency + bandwidth/2 - 120

    request.requestSpectrum(low_downlink_frequency, high_downlink_frequency,
                            100)
    request.requestSpectrum(low_uplink_frequency, high_uplink_frequency, 100)

    channel_setup_format_string = ("channel_setup-{n_prb}-{earfcn}-{ul_amp}-"
                                    "{dl_gain}")
    installs.append(channel_setup_format_string.format(n_prb=n_prb,
                                                       earfcn=earfcn,
                                                       ul_amp=ul_amp,
                                                       dl_gain=dl_gain))


for frequency_range in params.frequency_ranges:
    request.requestSpectrum(frequency_range.frequency_low,
                            frequency_range.frequency_high,
                            100)


if params.install_srslte:
    installs.append("srslte")

if params.install_gnuradio:
    installs.append("gnuradio")

if params.install_gnuradio_companion:
    installs.append("gnuradio-companion")

for i, x310_radio in enumerate(params.x310_radios):
    x310_node_pair(i, x310_radio, params.x310_pair_nodetype, installs)

for i, b210_node in enumerate(params.b210_nodes):
    b210_nuc_pair(i, b210_node, installs)


portal.context.printRequestRSpec()
