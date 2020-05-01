// Ryan Alder
// Spring, 2020
// Honors Thesis

/*
 * The purpose of this program is to observe the data rate adjustments
 * as a device moves away from a gateway
 */

#include "ns3/forwarder-helper.h"
#include "ns3/network-server-helper.h"
#include "ns3/lora-channel.h"
#include "ns3/mobility-helper.h"
#include "ns3/lora-phy-helper.h"
#include "ns3/lorawan-mac-helper.h"
#include "ns3/lora-helper.h"
#include "ns3/gateway-lora-phy.h"
#include "ns3/periodic-sender.h"
#include "ns3/periodic-sender-helper.h"
#include "ns3/log.h"
#include "ns3/string.h"
#include "ns3/command-line.h"
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/lora-device-address-generator.h"
#include "ns3/random-variable-stream.h"
#include "ns3/config.h"
#include "ns3/rectangle.h"

using namespace ns3;
using namespace lorawan;

NS_LOG_COMPONENT_DEFINE("FencelessGrazing");

// Trace sources that are called when a node changes its DR or TX power
void OnDataRateChange (uint8_t oldDr, uint8_t newDr) {
  NS_LOG_DEBUG ("DR" << unsigned(oldDr) << " -> DR" << unsigned(newDr));
}
void OnTxPowerChange (double oldTxPower, double newTxPower) {
  NS_LOG_DEBUG (oldTxPower << " dBm -> " << newTxPower << " dBm");
}

int main(int argc, char *argv[]) {
  // device properties
  int nDevices = 1;
  int nPeriods = 134;
  double sideLength = 80000.0;  // m
  std::string adrType = "ns3::AdrComponent";

  // introduce command line arguments to allow for our script to run simulations
  CommandLine cmd;
  cmd.AddValue("nDevices", "Number of end-nodes to simulate", nDevices);
  cmd.AddValue("PeriodsToSimulate", "Number of periods to simulate", nPeriods);
  cmd.AddValue("SideLength", "Length/width of the rectangle", sideLength);
  cmd.Parse(argc, argv);

  LogComponentEnable("AdrComponent", LOG_LEVEL_ALL);
  LogComponentEnableAll(LOG_PREFIX_FUNC);
  LogComponentEnableAll(LOG_PREFIX_NODE);
  LogComponentEnableAll(LOG_PREFIX_TIME);

  // Set the EDs to require Data Rate control from the NS
  Config::SetDefault("ns3::EndDeviceLorawanMac::DRControl", BooleanValue(true));

  // Create the wireless channel
  // http://samer.lahoud.fr/pub-pdf/jiot-19.pdf
  Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
  loss->SetPathLossExponent(3.033);
  loss->SetReference(1, 7.7);

  Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
  Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);

  // End device mobility
  MobilityHelper mobilityEd, mobilityGw;
  Ptr<ListPositionAllocator> allocator_ed = CreateObject<ListPositionAllocator>();
  allocator_ed->Add(Vector(0.0, 0.0, 0.0));
  mobilityEd.SetPositionAllocator(allocator_ed);

  // Gateway mobility
  Ptr<ListPositionAllocator> allocator = CreateObject<ListPositionAllocator>();
  allocator->Add(Vector(0.0, 0.0, 5.0)); // 5m off the ground
  mobilityGw.SetPositionAllocator(allocator);

  // Setup the helpers
  LoraPhyHelper phyHelper = LoraPhyHelper();
  phyHelper.SetChannel(channel);

  LorawanMacHelper macHelper = LorawanMacHelper();

  LoraHelper helper = LoraHelper();
  helper.EnablePacketTracking();

  // Create the gateways
  NodeContainer gateways;
  gateways.Create(1);
  mobilityGw.Install(gateways);
  phyHelper.SetDeviceType(LoraPhyHelper::GW);
  macHelper.SetDeviceType(LorawanMacHelper::GW);
  helper.Install(phyHelper, macHelper, gateways);

  // Create the end-nodes
  NodeContainer endNodes;
  endNodes.Create(1);
  mobilityEd.SetMobilityModel ("ns3::RandomWalk2dMobilityModel",
                               "Bounds", RectangleValue (Rectangle (-sideLength, sideLength,
                                                                    -sideLength, sideLength)),
                               "Distance", DoubleValue (40000),
                               "Speed", PointerValue(CreateObjectWithAttributes<UniformRandomVariable>
                               ("Min", DoubleValue(5.0), "Max", DoubleValue(5.0))));
  mobilityEd.Install(endNodes);

  uint8_t nwkId = 54;
  uint32_t nwkAddr = 1864;
  Ptr<LoraDeviceAddressGenerator> addrGen = CreateObject<LoraDeviceAddressGenerator> (nwkId, nwkAddr);

  phyHelper.SetDeviceType(LoraPhyHelper::ED);
  macHelper.SetDeviceType(LorawanMacHelper::ED_A);
  macHelper.SetAddressGenerator(addrGen);
  macHelper.SetRegion(LorawanMacHelper::EU);
  helper.Install(phyHelper, macHelper, endNodes);

  int appPeriodSeconds = 60; // one packet every minute
  PeriodicSenderHelper appHelper = PeriodicSenderHelper();
  appHelper.SetPeriod(Seconds(appPeriodSeconds));
  appHelper.SetPacketSize(12);
  ApplicationContainer appContainer = appHelper.Install(endNodes);

  // Create the NS
  NodeContainer networkServers;
  networkServers.Create(1);

  NetworkServerHelper networkServerHelper;
  networkServerHelper.SetGateways(gateways);
  networkServerHelper.SetEndDevices(endNodes);
  networkServerHelper.EnableAdr(true);
  networkServerHelper.SetAdr(adrType);
  networkServerHelper.Install(networkServers);

  // Install the forwarder on the gateways
  ForwarderHelper forwarderHelper;
  forwarderHelper.Install(gateways);

  // connect the traces
  Config::ConnectWithoutContext ("/NodeList/*/DeviceList/0/$ns3::LoraNetDevice/Mac/$ns3::EndDeviceLorawanMac/TxPower",
                                 MakeCallback (&OnTxPowerChange));
  Config::ConnectWithoutContext ("/NodeList/*/DeviceList/0/$ns3::LoraNetDevice/Mac/$ns3::EndDeviceLorawanMac/DataRate",
                                 MakeCallback (&OnDataRateChange));


  Time stateSamplePeriod = Seconds(60);
  helper.EnablePeriodicDeviceStatusPrinting(endNodes, gateways,
                                            "nodeData.txt", stateSamplePeriod);
  helper.EnablePeriodicPhyPerformancePrinting(gateways, "phyPerformance.txt",
                                              stateSamplePeriod);
  helper.EnablePeriodicGlobalPerformancePrinting("globalPerformance.txt",
                                                 stateSamplePeriod);
  LoraPacketTracker& tracker = helper.GetPacketTracker();

  Time simulationTime = Seconds(60 * nPeriods);
  Simulator::Stop(simulationTime);
  Simulator::Run();
  Simulator::Destroy();


  std::ofstream file;
  file.open("total.txt");
  file << tracker.CountMacPacketsGlobally(Seconds(0), Seconds(600 * (nPeriods+1))) << std::endl;
  file.close();
  return 0;
}
