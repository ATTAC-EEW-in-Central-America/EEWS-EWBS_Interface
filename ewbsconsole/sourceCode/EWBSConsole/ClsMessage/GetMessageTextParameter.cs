using EWBSConsole.ClzMain;
using System;
using System.Collections.Generic;

namespace Apl
{
    namespace Message
    {
        /// <summary>
        /// GetMessageTextParameter class
        /// </summary>
        public class GetMessageTextParameter
        {
            const string EncodCode = "iso-8859-1";

            const int AreaCodeMinNum = 1;                       // Area code minimum number
            const int AreaCodeMaxNum = 125;                     // Area code maximum number
            const int AreaCodeMinVal = 0x000;                   // Area code minimum value
            const int AreaCodeMaxVal = 0xFFE;                   // Area code maximum value
            const int MsgMinNum = 1;                            // Message mnimum number
            const int MsgMaxNum = 260;                          // Message maximum number
            const int TransmitTimeMinVal = 10;                  // Transmit time mnimum value
            const int TransmitTimeMaxVal = 86400;               // Transmit time maxmum value
            const int TransmitTimeInfiniteVal = -1;             // Transmit time infinite value

            /// <summary>
            /// Determine whether it is a hexadecimal character string
            /// </summary>
            /// <param name="str">Hexadecimal character</param>
            /// <returns>Return
            ///     true  : Normal
            ///     false : Error
            /// </returns>
            public static bool IsHexString(string str)
            {
                try
                {
                    if (string.IsNullOrEmpty(str))
                        return false;

                    foreach (char c in str)
                    {
                        if (!Uri.IsHexDigit(c))
                            return false;
                    }
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                    return false;
                }
                finally
                {
                }
            }

            /// <summary>
            /// Split area code
            /// </summary>
            /// <param name="areaCode">Area code</param>
            /// <param name="splitAreaCodeList">Split area code list</param>
            /// <returns>Result
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string SplitAreaCode(string areaCode, ref List<int> splitAreaCodeList)
            {
                try
                {
                    if (string.IsNullOrEmpty(areaCode))
                        return "Area code is not set.";

                    string[] areaCodes = areaCode.Split(' ');
                    List<int> areaCodeListTemp = new List<int>();

                    foreach (string acs in areaCodes)
                    {
                        if (!string.IsNullOrEmpty(acs))
                        {
                            if (GetMessageTextParameter.IsHexString(acs) == false)
                                return string.Format("Area code must be set in hexadecimal. {0}", acs);

                            int acn;
                            try
                            {
                                acn = Convert.ToInt32(acs, 16);
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine(ex.Message);
                                //Console.WriteLine(ex.StackTrace);
                                return string.Format("Area code value is too large. {0}", acs);
                            }

                            if (acn < AreaCodeMinVal || acn > AreaCodeMaxVal)
                                return string.Format("Set the area code within the range of 0x{0} to 0x{1}. {2}", string.Format("{0:X3}", AreaCodeMinVal), string.Format("{0:X3}", AreaCodeMaxVal), acs);

                            if (areaCodeListTemp.Contains(acn) == true)
                                return string.Format("The same area code is set. {0}", acs);

                            if (areaCodeListTemp.Count >= AreaCodeMaxNum)
                                return string.Format("The area code is set to exceed {0} cases.", string.Format("{0:d}", AreaCodeMaxNum));

                            areaCodeListTemp.Add(acn);
                        }
                    }

                    if (areaCodeListTemp.Count == 0)
                        return "Can not get an area code.";

                    splitAreaCodeList = areaCodeListTemp;
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
            /// Encode message
            /// </summary>
            /// <param name="msg">Message</param>
            /// <param name="encMsg">Encode message</param>
            /// <returns>Return
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string EncodeMessage(string msg, ref byte[] encMsg)
            {
                try
                {
                    System.Text.Encoding enc = System.Text.Encoding.GetEncoding(EncodCode);
                    byte[] msgBytes = enc.GetBytes(msg);
                    if (msgBytes.Length < MsgMinNum || msgBytes.Length > MsgMaxNum)
                    {
                        return string.Format("Please set the message within the range of {0} to {1} characters.", string.Format("{0:d}", MsgMinNum), string.Format("{0:d}", MsgMaxNum));
                    }

                    encMsg = msgBytes;
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
            /// Parse transmit time
            /// </summary>
            /// <param name="time">Transmit time</param>
            /// <param name="prsTime">Parse transmit time</param>
            /// <returns>Return
            ///     null  : Normal
            ///     !null : Error contents
            /// </returns>
            public static string ParseTransmitTime(string time, ref Int32 prsTime)
            {
                try
                {
                    Int32 timeTemp;
                    if (!Int32.TryParse(time, out timeTemp))
                        return "Unable to get transmit time.";

                    if (!(timeTemp == TransmitTimeInfiniteVal || (timeTemp >= TransmitTimeMinVal && timeTemp <= TransmitTimeMaxVal)))
                        return string.Format("Please set the transmit time within the range of {0} to {1} sec(or {2} : infinite time).", TransmitTimeMinVal.ToString(), TransmitTimeMaxVal.ToString(), TransmitTimeInfiniteVal.ToString());

                    prsTime = timeTemp;
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
