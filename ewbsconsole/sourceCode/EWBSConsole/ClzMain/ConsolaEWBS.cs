using System;
using System.Collections.Generic;
using Apl.Settings;
using Apl.Message;
using Apl.NetWork;
using System.IO;
using System.Threading;
using CommandLine;
using Apl.Log;
using System.Globalization;
using System.Text;
using System.Linq;
using System.Threading.Tasks;

namespace EWBSConsole.ClzMain
{
    class ConsolaEWBS
    {
        public static DateTime inicio = DateTime.UtcNow;
        public static DateTime fin = DateTime.UtcNow;


        public static string AppPathMnf = @"\EwbsConsole";
        public static string AppPathSft = @"\EwbsConsole";
        public static string AppPathFld = @"\AppFile";
        public static string ExceptLogDateFormat = "yyyy/MM/dd HH:mm:ss.fff tt";
        public static string ExceptLogExt = "_Except.log";

        public static string path()
        {
            if (!Directory.Exists(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + AppPathMnf + AppPathSft + AppPathFld))
            {
                Directory.CreateDirectory(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + AppPathMnf + AppPathSft + AppPathFld);
            }
            return Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + AppPathMnf + AppPathSft + AppPathFld + @"\" + DateTime.UtcNow.ToString("yyyyMMdd") + ExceptLogExt;
        }

        const string EwbsXmlSettingFileName = @"\ewbsconsole_xml_settings.config";
        //const string NmbsXmlSettingFileName = @"\nmbs_xml_settings.config";

        private List<Boton> botones = new List<Boton>();

        private string ewbsComputerName;
        private string areaCode = "000 001 002";
        private int alertLevelSelectedIndex;
        private List<string> alertLevel = new List<string>();
        private string alertMessage;
        private int ewbsTimer = 0;
        private bool tieneTimer = false;

        string[] EwbsXmlSettingInitVal = new string[]
        {
            "Please set the Computer Name(or IP Address)",  // EWBS TCP server computer name(or IP Address)
            "65504",                                        // EWBS TCP server port number (Not rewritable)
            "000 001 002",                                  // Area code (example)
            "0",                                            // Special Warning (example)
            "Alert Message"                                 // Alert message (example)
        };

        string[] NmbsXmlSettingInitVal = new string[]
        {
            "Please set the Computer Name(or IP Address)",  // NMBS TCP server computer name(or IP Address)
            "65520",                                        // NMBS TCP server port number (Not rewritable)
            "-1",                                           // Infinite time (example)
            "1",                                            // Important Notification (example)
            "7",                                            // White (example)
            "0",                                            // OFF (example)
            "Character super"                               // Character super (example)
        };

        const int SaveExceptLogFileNum = 6;                 // Save except log files number
        const int MsgHdrLen = 5;                            // Message header length
        const int TransmitStartCode = 0x01;                 // Transmit start code
        const int TransmitStopCode = 0x02;                  // Transmit stop code
        const int InqTransmitStatusCode = 0x03;             // Inquire transmit status code

        //private List<Button> Button = new List<Button>();   // Button controls list

        private string AppFolderPath = null;                // Application folder path
        private XmlSettings EwbsXmlSettings = null;         // Ewbs xml settings

        public int EwbsTimer
        {
            get
            {
                return ewbsTimer;
            }
            set
            {
                ewbsTimer = value;
            }
        }

        public bool TieneTimer
        {
            get { return tieneTimer; }
            set { tieneTimer = value; }
        }

        public string EwbsComputerName
        {
            get
            {
                return ewbsComputerName;
            }

            set
            {
                ewbsComputerName = value;
            }
        }

        public string AreaCode
        {
            get
            {
                return areaCode;
            }

            set
            {
                areaCode = value;
            }
        }

        public int AlertLevelSelectedIndex
        {
            get
            {
                return alertLevelSelectedIndex;
            }

            set
            {
                alertLevelSelectedIndex = value;
            }
        }

        public string AlertMessage
        {
            get
            {
                return alertMessage;
            }

            set
            {
                alertMessage = value;
            }
        }

        //private XmlSettings NmbsXmlSettings = null;         // Nmbs xml settings

        /// <summary>
        /// Main window
        /// </summary>
        public ConsolaEWBS()
        {



        }


        public void CargarCosas()
        {

            try
            {

                CargarAlertasBotones();

                //Console.WriteLine("Mario 1");
                // Create application folder
                AppFolderPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + AppPathMnf + AppPathSft + AppPathFld;
                //Console.WriteLine("Mario 2");
                if (!Directory.Exists(AppFolderPath))
                {
                    DirectoryInfo di = Directory.CreateDirectory(AppFolderPath);
                }
                //Console.WriteLine("Mario 3");
                // Start collecting exception logs
                //DateTime dt = DateTime.UtcNow;
                //string ExceptLogPathFileName = AppFolderPath + @"\" + dt.ToString("yyyyMMdd_HHmmss") + ExceptLogExt;
                //string ExceptLogPathFileName = AppFolderPath + @"\" + dt.ToString("yyyyMMdd") + ExceptLogExt;

                //ExceptLog.StartExceptLogCollect(ExceptLogPathFileName, SaveExceptLogFileNum);
                //Console.WriteLine(dt.ToString(ExceptLogDateFormat) + " start");

                // Read ewbs settings file
                EwbsXmlSettings = new XmlSettings();
                EwbsXmlSettings.ReadXmlSettingFile(AppFolderPath + EwbsXmlSettingFileName, ref EwbsXmlSettings);
                if (string.IsNullOrEmpty(EwbsXmlSettings.Value[0]))
                {
                    // Initialization ewbs settings
                    for (int i = 0; i < EwbsXmlSettingInitVal.Length; i++)
                        EwbsXmlSettings.Value[i] = EwbsXmlSettingInitVal[i];
                }
                ewbsComputerName = EwbsXmlSettings.Value[0];
                areaCode = EwbsXmlSettings.Value[2];
                alertLevelSelectedIndex = int.Parse(EwbsXmlSettings.Value[3]);
                alertMessage = EwbsXmlSettings.Value[4];
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                //Console.WriteLine(ex.StackTrace);
            }
        }

        public static string ExtraerTexto(string texto)
        {
            string txt = "";

            if (texto.Contains("<identifier>"))
            {
                txt = texto.Replace("<identifier>", "").Replace("</identifier>", "");
            }

            if (texto.Contains("value"))
            {
                txt = texto.Replace("<value>", "").Replace("</value>", "");
            }

            if (texto.Contains("headline"))
            {
                txt = texto.Replace("<headline>", "").Replace("</headline>", "");
            }
            
            txt = string.IsNullOrWhiteSpace(txt) ? "" : txt.Trim();
            return txt;
        }

        public static string[] ReadLines(string path)
        {
            //string path2 = AppDomain.CurrentDomain.BaseDirectory + "events.txt"; 
            //bool bandera = true;

            //while (bandera)
            //{
            //    try
            //    {
            //        File.Copy(path, path2, true);
            //        bandera = false;
            //    }
            //    catch (IOException iox)
            //    {
            //        Console.WriteLine(iox.Message);
            //    }
            //}
            REINTENTAR:
            try
            {                
                    using (var fs = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite))
                    using (var sr = new StreamReader(fs, Encoding.UTF8))
                    {
                        List<string> lines = new List<string>();
                        string line = "";
                        while ((line = sr.ReadLine()) != null)
                        {
                            lines.Add(line);
                        }

                        return lines.ToArray();
                    }
            }
            catch
            {
                goto REINTENTAR;
            }
        }

        public static string[] ReadLines2(string path)
        {
            //using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
            using (var sr = new StreamReader(File.Open(path,
                           FileMode.Open,
                           FileAccess.Read,
                           FileShare.ReadWrite)))
            {
                List<string> lines = new List<string>();
                string line = "";
                while ((line = sr.ReadLine()) != null)
                {
                    lines.Add(line);
                }

                return lines.ToArray();
            }
        }

        internal static DateTime ConvertirFecha(string fecha)
        {
            return DateTime.Parse(fecha);
        }

        public string EwbsEvents()
        {
            Int64 position = 0;
            string ruta = AppDomain.CurrentDomain.BaseDirectory + "events.txt";

            string str = "";

            string[] initial = File.ReadAllLines(ruta);
            string[] current = initial;
            string[] sub_current;
            int sub_current_index = 0;
            while (true)
            {
                current = ReadLines(ruta);
                if (current.Length != initial.Length)
                {
                    sub_current = new string[current.Length - initial.Length];
                    sub_current_index = 0;
                    for (int i = initial.Length; i < current.Length; i++)
                    {
                        sub_current[sub_current_index] = current[i];
                        sub_current_index = sub_current_index + 1;
                    }

                    foreach (var line in sub_current)
                    {
                        if (line.Contains("<headline>"))
                        {
                            //para sacar titular
                            str += ExtraerTexto(line);
                            try
                            {
                                //para sacar recomendaciones
                                str += ExtraerTexto(sub_current[position + 1]);
                            }
                            catch (Exception) { }
                            position = position + 1;
                            break;
                        }
                    }
                    initial = current;
                }
            }
        }

        public void CargarAlertasBotones()
        {
            botones.Clear();
            botones.Add(new Boton("Boton1", "Confirmar Conexión", "1"));
            botones.Add(new Boton("Boton2", "Comenzar Transmisión", "2"));
            botones.Add(new Boton("Boton3", "Consultar Estado", "3"));
            botones.Add(new Boton("Boton4", "Parar Transmisión", "4"));
            botones.Add(new Boton("Boton5", "Ver Folder", "5"));
            botones.Add(new Boton("Boton6", "Salir", "6"));

            alertLevel.Clear();
            alertLevel.Add("Special Warning");
            alertLevel.Add("Normal Warning");

            alertLevelSelectedIndex = 1;
        }

        public Boton getBotonIndex(int i)
        {
            return botones[i];
        }
        public static string FormatFecha(DateTime fechaParam)
        {
            
            return fechaParam.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ");
        }

        public static string CalcularTimeSpan(DateTime start, DateTime end)
        {
            TimeSpan t = end - start;

            return t.TotalSeconds.ToString("#0.000", CultureInfo.InvariantCulture);

        }

        public void CierreDeAplicacion()
        {
            #region Closed window
            try
            {
                // Write ewbs settings file
                EwbsXmlSettings.Value[0] = ewbsComputerName;
                EwbsXmlSettings.Value[2] = areaCode;
                EwbsXmlSettings.Value[3] = alertLevelSelectedIndex.ToString();
                EwbsXmlSettings.Value[4] = alertMessage;
                EwbsXmlSettings.WriteSettingFile(AppFolderPath + EwbsXmlSettingFileName, EwbsXmlSettings);

                //// Write nmbs settings file
                //NmbsXmlSettings.Value[0] = nmbsComputerName.Text;
                //NmbsXmlSettings.Value[2] = transmitTime.Text;
                //NmbsXmlSettings.Value[3] = characterSuperLevel.SelectedIndex.ToString();
                //NmbsXmlSettings.Value[4] = foregroundColor.SelectedIndex.ToString();
                //NmbsXmlSettings.Value[5] = builtInSound.SelectedIndex.ToString();
                //NmbsXmlSettings.Value[6] = characterSuper.Text;
                //NmbsXmlSettings.WriteSettingFile(AppFolderPath + NmbsXmlSettingFileName, NmbsXmlSettings);

                // Clear button controls list
                //Button.Clear();

                // End except log collect
                DateTime dt = DateTime.UtcNow;
                //Console.WriteLine(dt.ToString(ExceptLogDateFormat) + " end");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(System.DateTime.UtcNow), ConsolaEWBS.path(), ex.Message);
                ////Console.WriteLine(ex.StackTrace);
            }
            finally
            {
            }
            #endregion
        }

        /// <summary>
        /// Button click event handler
        /// </summary>
        /// <param name="sender">Event source object</param>
        /// <param name="e">Event supplement information</param>
        public void ejecutarAcciones(Boton sender)
        {
            try
            {
                inicio = DateTime.UtcNow;
                // If control is enabled
                Boton target = sender;
                int tagNo = 0;
                if (target != null && target.Tag != null && int.TryParse(target.Tag.ToString(), out tagNo))
                {
                    string computerName = null;
                    string portNum = null;
                    string caption = null;
                    byte[] msgTemp = null;
                    byte[] transmitMsgBytes = null;
                    string rc = null;


                    // Get EWBS Inserter terminal computerName & port number
                    computerName = ewbsComputerName;
                    portNum = EwbsXmlSettings.Value[1];



                    // Button click process
                    switch (tagNo)
                    {
                        case 1:     // Confirm connect button click
                            // Check TCP server connect
                            caption = "Confirm Connect";
                            transmitMsgBytes = new byte[0];
                            break;

                        case 2:     // Start transmit button click


                            // Start transmit to EWBS
                            //areaCode = "";
                            //for (int i = 0; i < 125; i++)
                            //    areaCode += string.Format("{0:X3} ", i);

                            caption = "Start Transmit";
                            msgTemp = new byte[0x0300];
                            rc = CreatMessage.CreationEwbsStartTransmitMessage(MsgHdrLen, TransmitStartCode, areaCode, alertLevelSelectedIndex, alertMessage, ref msgTemp);
                            if (rc != null)
                            {

                                Console.WriteLine("Alert " + caption + ": " + rc);
                                return;
                            }
                            transmitMsgBytes = new byte[((int)msgTemp[0] << 8) + (int)msgTemp[1]];
                            Array.Copy(msgTemp, transmitMsgBytes, transmitMsgBytes.Length);
                            break;

                        case 3:     // Transmit status inquiry button click
                            // Transmit status inquiry
                            caption = "Transmit Status Inquiry";
                            EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(System.DateTime.UtcNow), ConsolaEWBS.path(), caption);
                            msgTemp = new byte[0x0010];
                            rc = CreatMessage.CreationFixedSizeMessage(MsgHdrLen, InqTransmitStatusCode, ref msgTemp);
                            if (rc != null)
                            {
                                //MessageBox.Show(c, caption, MessageBoxButton.OK, MessageBoxImage.Error);
                                Console.WriteLine("Alert: " + caption + ": " + rc);
                                return;
                            }
                            transmitMsgBytes = new byte[((int)msgTemp[0] << 8) + (int)msgTemp[1]];
                            Array.Copy(msgTemp, transmitMsgBytes, transmitMsgBytes.Length);
                            break;

                        case 4:     // Stop transmit button click
                            // Stop transmit
                            caption = "Stop Transmit";
                            msgTemp = new byte[0x0010];
                            rc = CreatMessage.CreationFixedSizeMessage(MsgHdrLen, TransmitStopCode, ref msgTemp);
                            if (rc != null)
                            {
                                //MessageBox.Show(rc, caption, MessageBoxButton.OK, MessageBoxImage.Error);
                                Console.WriteLine("Alert: " + caption + ": " + rc);
                                return;
                            }
                            transmitMsgBytes = new byte[((int)msgTemp[0] << 8) + (int)msgTemp[1]];
                            Array.Copy(msgTemp, transmitMsgBytes, transmitMsgBytes.Length);
                            break;

                        case 5:     // App folder button click
                            // Open application folder
                            System.Diagnostics.Process.Start("EXPLORER.EXE", AppFolderPath);
                            return;
                        default:
                            return;
                    }

                    // Background thread activation
                    object[] args = new object[5];
                    args[0] = caption;                  // Caption
                    args[1] = computerName;             // Computer name(or IP address)
                    args[2] = int.Parse(portNum);       // TCP server port number
                    args[3] = transmitMsgBytes;         // Transmit message
                    args[4] = transmitMsgBytes.Length;  // Transmit message length
                    Thread thrd = new Thread(new ParameterizedThreadStart(BackgroundThread));
                    thrd.IsBackground = true;
                    thrd.Start(args);


                    // Display transmit message

                    Console.WriteLine(FormatFecha(inicio) + ": Transmited Message: " + BitConverter.ToString(transmitMsgBytes, 0, transmitMsgBytes.Length).Replace("-", " "));
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(inicio), ConsolaEWBS.path(), "Transmited Message: " + BitConverter.ToString(transmitMsgBytes, 0, transmitMsgBytes.Length).Replace("-", " "));
                    thrd.Join();

                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(System.DateTime.UtcNow), ConsolaEWBS.path(), ex.Message);
                ////Console.WriteLine(ex.StackTrace);
            }
            finally
            {
            }
        }

        /// <summary>
        /// Background thread
        /// </summary>
        /// <param name="args">arguments
        ///     args[0] = Caption
        ///     args[1] = Computer name(or IP address)
        ///     args[2] = TCP server port number
        ///     args[3] = Transmit message
        ///     args[4] = Transmit message length
        /// </param>
        public static void BackgroundThread(object args)
        {
            try
            {
                // Eexpansion argument
                object[] argsTmp = (object[])args;

                // If TCP server connect confirm
                if ((string)argsTmp[0].ToString() == "Confirm Connect")
                {
                    // Check TCP server connect
                    string getIpAdr = null;
                    string rc1 = TcpServer.CheckTcpServerConnect((string)argsTmp[1].ToString(), ref getIpAdr);
                    if (rc1 == null)
                    {
                        fin = DateTime.UtcNow;
                        Console.WriteLine(FormatFecha(fin) + ": " + (string)argsTmp[0].ToString() + ": " + "Succeeded connect." + " | Timespan Diff: " + CalcularTimeSpan(inicio, fin));

                        EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(fin), ConsolaEWBS.path(), (string)argsTmp[0].ToString() + ": " + "Succeeded connect.", CalcularTimeSpan(inicio, fin));
                        //MessageBox.Show("Succeeded connect.", (string)argsTmp[0].ToString(), MessageBoxButton.OK, MessageBoxImage.Information);
                    }
                    else
                    {
                        Console.WriteLine((string)argsTmp[0].ToString() + ": " + rc1);
                        fin = DateTime.UtcNow;
                        EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(fin), ConsolaEWBS.path(), "As " + (string)argsTmp[0].ToString() + ": " + rc1, CalcularTimeSpan(inicio, fin));
                        //MessageBox.Show(rc1, (string)argsTmp[0].ToString(), MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
                else
                {
                    // Request TCP server
                    int responseMsgLen = 0;
                    byte[] responseMsgBytes = new byte[0x0300];
                    string rc = TcpServer.RequestTcpServer((string)argsTmp[1].ToString(), (int)argsTmp[2], (byte[])argsTmp[3], (int)argsTmp[4], ref responseMsgBytes, ref responseMsgLen);
                    if (rc == null)
                    {
                        fin = DateTime.UtcNow;
                        Console.WriteLine(FormatFecha(fin) + ": Response Message: " + BitConverter.ToString(responseMsgBytes, 0, responseMsgLen).Replace("-", " ") + " " + (string)argsTmp[0].ToString() + " | Timespan Diff: " + CalcularTimeSpan(inicio, fin));

                        EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(fin), ConsolaEWBS.path(), "Response Message: " + BitConverter.ToString(responseMsgBytes, 0, responseMsgLen).Replace("-", " ") + " " + (string)argsTmp[0].ToString(), CalcularTimeSpan(inicio, fin));
                        //MessageBox.Show("Response Message.\r\n" + BitConverter.ToString(responseMsgBytes, 0, responseMsgLen).Replace("-", " "), (string)argsTmp[0].ToString(), MessageBoxButton.OK, MessageBoxImage.Information);
                    }
                    else
                    {

                        Console.WriteLine((string)argsTmp[0].ToString() + ": " + rc);
                        fin = DateTime.UtcNow;

                        EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(fin), ConsolaEWBS.path(), (string)argsTmp[0].ToString() + ": " + rc, CalcularTimeSpan(inicio, fin));
                        //MessageBox.Show(rc, (string)argsTmp[0].ToString(), MessageBoxButton.OK, MessageBoxImage.Error);
                    }

                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                EWBSConsole.ClsLog.LogCustom.AlternativeLog(FormatFecha(DateTime.UtcNow), ConsolaEWBS.path(), ex.Message);
                //Console.WriteLine(ex.StackTrace);
            }
            finally
            {
            }
        }


    }

    class Boton
    {
        string nombre;
        string texto;
        string tag;

        public string Nombre
        {
            get
            {
                return nombre;
            }

            set
            {
                nombre = value;
            }
        }

        public string Texto
        {
            get
            {
                return texto;
            }

            set
            {
                texto = value;
            }
        }

        public string Tag
        {
            get
            {
                return tag;
            }

            set
            {
                tag = value;
            }
        }

        public Boton(string name, string text, string tag)
        {
            nombre = name;
            texto = text;
            this.tag = tag;
        }
    }

}
