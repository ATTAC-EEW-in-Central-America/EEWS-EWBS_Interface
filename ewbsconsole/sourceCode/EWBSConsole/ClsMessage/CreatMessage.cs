using EWBSConsole.ClzMain;
using System;
using System.Collections.Generic;

namespace Apl
{
    namespace Message
    {
        /// <summary>
        /// CreatMessage class
        /// </summary>
        public class CreatMessage
        {
            /// <summary>
            /// Creation ewbs start transmit message
            /// </summary>
            /// <param name="msgHdrLen">Message header length</param>
            /// <param name="reqCode">Request code</param>
            /// <param name="areaCode">Area code</param>
            /// <param name="alertLevel">Alert level</param>
            /// <param name="alertMessage">Alert message</param>
            /// <param name="crtMsg">Creation message</param>
            /// <returns>Result
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string CreationEwbsStartTransmitMessage(int msgHdrLen, int reqCode, string areaCode, int alertLevel, string alertMessage, ref byte[] crtMsg)
            {
                try
                {
                    // Creation EWBS start transmit message
                    crtMsg[0x00] = 0x00;
                    crtMsg[0x01] = 0x00;
                    crtMsg[0x02] = 0x00;
                    crtMsg[0x03] = 0x00;
                    crtMsg[0x04] = (byte)reqCode;
                    crtMsg[0x05] = 0x00;
                    int mgLen = msgHdrLen + 1;

                    // Set area codes
                    List<int> areaCodeList = new List<int>();
                    string rc = GetMessageTextParameter.SplitAreaCode(areaCode, ref areaCodeList);
                    if (rc != null)
                        return rc;
                    foreach (int ac in areaCodeList)
                    {
                        crtMsg[mgLen + 0] = (byte)(ac >> 8);
                        crtMsg[mgLen + 1] = (byte)(ac);
                        mgLen += 2;
                    }

                    // Set area codes number
                    crtMsg[msgHdrLen] = (byte)areaCodeList.Count;

                    // Set alert level
                    crtMsg[mgLen] = (byte)alertLevel;
                    mgLen++;

                    // Set alert message
                    byte[] msg = new byte[0x0200];
                    rc = GetMessageTextParameter.EncodeMessage(alertMessage, ref msg);
                    if (rc != null)
                        return rc;
                    Buffer.BlockCopy(msg, 0, crtMsg, mgLen, msg.Length);
                    mgLen += msg.Length;

                    // Set message length
                    crtMsg[0x00] = (byte)(mgLen >> 8);
                    crtMsg[0x01] = (byte)(mgLen);
                    return null;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                    return "Exception occured. Please refer to the exception log.";
                }
                finally
                {
                }
            }

            /// <summary>
            /// Creation nmbs start transmit message
            /// </summary>
            /// <param name="msgHdrLen">Message header length</param>
            /// <param name="reqCode">Request code</param>
            /// <param name="transmitTime">Transmit time</param>
            /// <param name="characterSuperLevel">Character super level</param>
            /// <param name="foregroundColor">Foreground color</param>
            /// <param name="builtInSound">Built-in sound</param>
            /// <param name="characterSuper">Character super</param>
            /// <param name="crtMsg">Creation message</param>
            /// <returns>Result
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string CreationNmbsStartTransmitMessage(int msgHdrLen, int reqCode, string transmitTime, int characterSuperLevel, int foregroundColor, int builtInSound, string characterSuper, ref byte[] crtMsg)
            {
                try
                {
                    // Creation NMBS start transmit message
                    crtMsg[0x00] = 0x00;
                    crtMsg[0x01] = 0x00;
                    crtMsg[0x02] = 0x00;
                    crtMsg[0x03] = 0x00;
                    crtMsg[0x04] = (byte)reqCode;
                    int mgLen = msgHdrLen;

                    // Set Transmit time
                    Int32 prsTime = 0;
                    string rc = GetMessageTextParameter.ParseTransmitTime(transmitTime, ref prsTime);
                    if (rc != null)
                        return rc;
                    crtMsg[mgLen + 0] = (byte)(prsTime >> 24);
                    crtMsg[mgLen + 1] = (byte)(prsTime >> 16);
                    crtMsg[mgLen + 2] = (byte)(prsTime >> 8);
                    crtMsg[mgLen + 3] = (byte)(prsTime);
                    mgLen += 4;

                    // Set character super level
                    crtMsg[mgLen] = (byte)characterSuperLevel;
                    mgLen++;

                    // Set foreground color
                    crtMsg[mgLen] = (byte)foregroundColor;
                    mgLen++;

                    // Set built in sound
                    if (characterSuperLevel == 0)
                        crtMsg[mgLen] = (byte)builtInSound;
                    else
                        crtMsg[mgLen] = 0;
                    mgLen++;

                    // Set alert message
                    byte[] msg = new byte[0x0200];
                    rc = GetMessageTextParameter.EncodeMessage(characterSuper, ref msg);
                    if (rc != null)
                        return rc;
                    Buffer.BlockCopy(msg, 0, crtMsg, mgLen, msg.Length);
                    mgLen += msg.Length;

                    // Set message length
                    crtMsg[0x00] = (byte)(mgLen >> 8);
                    crtMsg[0x01] = (byte)(mgLen);
                    return null;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                    return "Exception occured. Please refer to the exception log.";
                }
                finally
                {
                }
            }

            /// <summary>
            /// Creation fixed size message
            /// </summary>
            /// <param name="msgHdrLen">Message header length</param>
            /// <param name="reqCode">Request code</param>
            /// <param name="crtMsg">Creation message</param>
            /// <returns>Result
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string CreationFixedSizeMessage(int msgHdrLen, int reqCode, ref byte[] crtMsg)
            {
                try
                {
                    // Creation fixed size message
                    crtMsg[0x00] = (byte)(msgHdrLen >> 8);
                    crtMsg[0x01] = (byte)(msgHdrLen);
                    crtMsg[0x02] = 0x00;
                    crtMsg[0x03] = 0x00;
                    crtMsg[0x04] = (byte)reqCode;
                    return null;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                    return "Exception occured. Please refer to the exception log.";
                }
                finally
                {
                }
            }
        }
    }
}
