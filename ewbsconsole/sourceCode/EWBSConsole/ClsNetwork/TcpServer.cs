using EWBSConsole.ClzMain;
using System;
using System.IO;
using System.Net;
using System.Net.Sockets;

namespace Apl
{
    namespace NetWork
    {
        /// <summary>
        /// TcpServer class
        /// </summary>
        public class TcpServer
        {
            const int NsWriteTimeout = 3000;        // Network stream write timeout value
            const int NsReadTimeout = 10000;        // Network stream read timeout value

            /// <summary>
            /// Check TCP server connect
            /// </summary>
            /// <param name="computerName">Computer name(or IP Address)</param>
            /// <param name="getIpAdr">Get IP Address</param>
            /// <returns>Result
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string CheckTcpServerConnect(string computerName, ref string getIpAdr)
            {
                IPAddress ipa;
                string ipAdr = "";
                System.Net.NetworkInformation.Ping p = null;
                try
                {
                    // Check if computer name (IP address) is set
                    if (string.IsNullOrEmpty(computerName))
                        return "Computer name(or IP address) is not set.";

                    // Check if it can be recognized as an IP address
                    if (System.Net.IPAddress.TryParse(computerName, out ipa))
                    {
                        // It can be recognized as an IP address
                        ipAdr = computerName;
                    }
                    else
                    {
                        // Obtain IP address from computer name
                        IPHostEntry iphe = Dns.GetHostEntry(computerName);
                        IPAddress[] addresses = iphe.AddressList;
                        foreach (IPAddress address in addresses)
                        {
                            // Acquire only IP vsersion 4
                            if (address.AddressFamily == AddressFamily.InterNetwork)
                            {
                                ipAdr = address.ToString();
                                break;
                            }
                        }

                        // Check if IP address was obtained from computer name
                        if (string.IsNullOrEmpty(ipAdr))
                            return "Can not get the IP address from the computer name.";
                    }

                    // Check if the specified IP address exists
                    p = new System.Net.NetworkInformation.Ping();
                    try
                    {
                        // Ping a specified IP address
                        System.Net.NetworkInformation.PingReply reply = p.Send(ipAdr);

                        // Check ping transmission status
                        if (!(reply.Status == System.Net.NetworkInformation.IPStatus.Success))
                            return "TCP server connection failed.";

#if false // for debugging
                    Console.WriteLine(string.Format("Reply from {0}:bytes={1} time={2}ms TTL={3}", reply.Address, reply.Buffer.Length, reply.RoundtripTime, reply.Options.Ttl));
#endif
                    }
                    catch
                    {
                        return "TCP server is not connected to the network.";
                    }

                    getIpAdr = ipAdr;
                    return null;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), ex.Message);

                    //Console.WriteLine(ex.StackTrace);
                    return "Exception occured. Please refer to the exception log.";
                }
                finally
                {
                    if (p != null)
                        p.Dispose();
                }
            }

            /// <summary>
            /// Request TCP server
            /// </summary>
            /// <param name="computerName">Computer name(or IP Address)</param>
            /// <param name="portNo">TCP server port number</param>
            /// <param name="transmitMsgBytes">Transmit message</param>
            /// <param name="transmitMsgLen">Transmit message length</param>
            /// <param name="responseMsgBytes">Response message</param>
            /// <param name="responseMsgLen">Response message length</param>
            /// <returns>Result
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string RequestTcpServer(string computerName, int portNo, byte[] transmitMsgBytes, int transmitMsgLen, ref byte[] responseMsgBytes, ref int responseMsgLen)
            {
                TcpClient tcp = null;
                NetworkStream ns = null;
                MemoryStream ms = null;
                try
                {
                    // Check TCP server connect
                    string getIpAdr = null;
                    string rc = TcpServer.CheckTcpServerConnect(computerName, ref getIpAdr);
                    if (rc != null)
                        return rc;

                    // Connect to a TCP server
                    try
                    {
                        tcp = new TcpClient(getIpAdr, portNo);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.Message);
                        EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), ex.Message);
                        //Console.WriteLine(ex.StackTrace);
                        return "Connection refused to target computer";
                    }

                    // Get network stream
                    ns = tcp.GetStream();

                    // Set read/write timeout
                    ns.ReadTimeout = NsReadTimeout;
                    ns.WriteTimeout = NsWriteTimeout;

                    // Write a request message
                    ns.Write(transmitMsgBytes, 0, transmitMsgLen);

                    // Receive response message from TCP server
                    ms = new MemoryStream();
                    byte[] resBytes = new byte[0x0300];
                    int msgSize = 0;
                    int sumSize = 0;
                    int resSize = 0;
                    do
                    {
                        // Receive part of the response message
                        resSize = ns.Read(resBytes, 0, resBytes.Length);

                        // When the response message length is 0, it is judged that the server has disconnected
                        if (resSize == 0)
                            return "TCP server has disconnected.";

                        // Extract message length
                        if (msgSize == 0)
                        {
                            byte[] tmpBytes = new byte[4];
                            Buffer.BlockCopy(resBytes, 0, tmpBytes, 2, 2);
                            if (BitConverter.IsLittleEndian)
                                Array.Reverse(tmpBytes);
                            msgSize = BitConverter.ToInt32(tmpBytes, 0);
                        }

                        // Accumulate response message
                        ms.Write(resBytes, 0, resSize);
                        sumSize += resSize;

                        // If there is still data to be read or the reception size is less than the message length, continue receiving
                    } while (ns.DataAvailable || sumSize < msgSize);

                    // Return response message
                    Buffer.BlockCopy(ms.GetBuffer(), 0, responseMsgBytes, 0, (int)ms.Length);
                    responseMsgLen = (int)ms.Length;
                    return null;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                    return "Exception occured. Please refer to the exception log.";
                }
                finally
                {
                    if (ms != null)
                        ms.Close();
                    if (ns != null)
                        ns.Close();
                    if (tcp != null)
                        tcp.Close();
                }
            }
        }
    }
}
