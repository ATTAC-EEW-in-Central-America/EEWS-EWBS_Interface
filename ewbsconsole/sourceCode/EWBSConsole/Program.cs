using CommandLine;
using EWBSConsole.ClzMain;
using System;
using System.Collections;
using System.IO;
using System.Configuration;

namespace EWBSConsole
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                args = new String[1];
                args[0] = "--help";
                ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), "Command: " + string.Join(" ", args));
            }
            else
            {
                ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), "Command: " + string.Join(" ", args));
            }
            Parser.Default.ParseArguments<ConnectOptions, SendOptions, CheckOptions, StopOptions, MonitorOptions,FolderOptions>(args)
                .WithParsed<ConnectOptions>(options => Connect(options))
                .WithParsed<SendOptions>(options => Send(options))
                .WithParsed<CheckOptions>(options => Check(options))
                .WithParsed<StopOptions>(options => Stop(options))
                .WithParsed<MonitorOptions>(options => Monitor(options))
                .WithParsed<FolderOptions>(options => Folder(options))
                .WithNotParsed(errors => HandleParseError(errors));

        }

        private static void Connect(ConnectOptions opts)
        {
            ConsolaEWBS main = new ConsolaEWBS();
            main.CargarCosas();

            if (!string.IsNullOrWhiteSpace(opts.IP))
            {
                main.EwbsComputerName = opts.IP;
            }

            main.ejecutarAcciones(main.getBotonIndex(0));
            main.CierreDeAplicacion();
        }

        private static void Send(SendOptions opts)
        {
            ConsolaEWBS main = new ConsolaEWBS();
            main.CargarCosas();


            string area = opts.Area;
            string emergencia = opts.Emergency;
            string mensaje = opts.Message;

            string timer = opts.Timer;
            string ip = opts.IP;

            if (!string.IsNullOrWhiteSpace(ip))
            {
                main.EwbsComputerName = ip;
            }

            try
            {
                if (!string.IsNullOrWhiteSpace(timer))
                {
                    
                    main.EwbsTimer = int.Parse(timer);
                    main.TieneTimer = true;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error during convertion of Timer into Number. " + ex.Message);
                ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), "Error during convertion of Timer into Number. " + ex.Message);
            }

            if (!string.IsNullOrWhiteSpace(area))
            {
                main.AreaCode = area;
            }
            try
            {
                if (!string.IsNullOrWhiteSpace(emergencia))
                {
                    main.AlertLevelSelectedIndex = int.Parse(emergencia.ToString())-1;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error during convertion of Alert Level into Number. " + ex.Message);
                ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), "Error during convertion of Alert Level into Number. " + ex.Message);
            }
            main.AlertMessage = mensaje;
            main.ejecutarAcciones(main.getBotonIndex(1));

            if (main.TieneTimer)
            {
                System.Threading.Thread.Sleep(TimeSpan.FromSeconds(main.EwbsTimer));

                main.ejecutarAcciones(main.getBotonIndex(3));
            }

            main.CierreDeAplicacion();
        }

        private static void Check(CheckOptions opts)
        {
            ConsolaEWBS main = new ConsolaEWBS();
            main.CargarCosas();
            string ip = opts.IP;
            if (!string.IsNullOrWhiteSpace(ip))
            {
                main.EwbsComputerName = ip;
            }
            main.ejecutarAcciones(main.getBotonIndex(2));
            main.CierreDeAplicacion();
        }

        private static void Stop(StopOptions opts)
        {
            ConsolaEWBS main = new ConsolaEWBS();
            main.CargarCosas();
            string ip = opts.IP;
            if (!string.IsNullOrWhiteSpace(ip))
            {
                main.EwbsComputerName = ip;
            }
            main.ejecutarAcciones(main.getBotonIndex(3));
            main.CierreDeAplicacion();
        }

        private static void Monitor(MonitorOptions opts)
        {
            ConsolaEWBS main = new ConsolaEWBS();           
            main.CargarCosas();
            
            //DATOS NUEVOS
            Int64 position = 0;
            string ruta = ConfigurationManager.AppSettings["RutaMonitor"];

            string headLineText = "";
            string idEvent = "";
            string magnitude = "";
            bool isMagCreationDate = false;
            DateTime magCreationDate = DateTime.UtcNow;
            DateTime sendDate = DateTime.UtcNow;
            DateTime receptionDate = DateTime.UtcNow;
            string aux = "";
            string aux2 = "";
            string[] initial = ConsolaEWBS.ReadLines(ruta);
            string[] current = initial;
            string[] subCurrent;
            string[] arrAux;
            int sub_current_index = 0;
            Int64 auxINT = 0;
            //DATOS NUEVOS

            string area = opts.Area;
            string emergencia = opts.Emergency;
            

            string timer = opts.Timer;
            string ip = opts.IP;

            if (!string.IsNullOrWhiteSpace(ip))
            {
                main.EwbsComputerName = ip;
            }

            try
            {
                if (!string.IsNullOrWhiteSpace(timer))
                {

                    main.EwbsTimer = int.Parse(timer);
                    main.TieneTimer = true;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error during convertion of Timer into Number. " + ex.Message);
                ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), "Error during convertion of Timer into Number. " + ex.Message);
            }

            if (!string.IsNullOrWhiteSpace(area))
            {
                main.AreaCode = area;
            }
            try
            {
                if (!string.IsNullOrWhiteSpace(emergencia))
                {
                    main.AlertLevelSelectedIndex = int.Parse(emergencia.ToString()) - 1;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error during convertion of Alert Level into Number. " + ex.Message);
                ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), "Error during convertion of Alert Level into Number. " + ex.Message);
            }

            //ITERACION INDEFINIDA

            DateTime ahora = DateTime.UtcNow;
            Console.WriteLine(ahora.ToString("dd-MM-yyyy hh:mm:ss.fff tt") + ": Started Monitoring messages from Stomp Events File.");
            ClsLog.LogCustom.AlternativeLog(ahora.ToString("dd-MM-yyyy hh:mm:ss.fff tt"), ConsolaEWBS.path(), "Started Monitoring messages from Stomp Events File.");

            try
            {

                while (true)
                {
                    current = ConsolaEWBS.ReadLines(ruta);

                    while(current.Length < initial.Length)
                    {
                        current = ConsolaEWBS.ReadLines(ruta);
                    }

                    if (current.Length != initial.Length)
                    {
                        subCurrent = new string[current.Length - initial.Length];
                        sub_current_index = 0;
                        for (int i = initial.Length; i < current.Length; i++)
                        {
                            subCurrent[sub_current_index] = current[i];
                            sub_current_index = sub_current_index + 1;
                        }

                        foreach (var line in subCurrent)
                        {
                            if (line.Contains("<identifier>"))
                            {
                                idEvent = ConsolaEWBS.ExtraerTexto(line);
                            }
                            auxINT = position + 1;
                            aux = line;
                            aux2 = subCurrent[auxINT];
                            if (aux.Contains("Current time") && aux2.Contains("alert"))
                            {
                                arrAux = line.Replace("Current time:", "").Replace("Sent time:", ",").Split(',');
                                receptionDate = ConsolaEWBS.ConvertirFecha(arrAux[0].Trim());
                                sendDate = ConsolaEWBS.ConvertirFecha(arrAux[1].Trim());
                            }

                            if (line.Contains("<value>"))
                            {
                                isMagCreationDate = true;
                                magCreationDate = ConsolaEWBS.ConvertirFecha(ConsolaEWBS.ExtraerTexto(line));
                            }

                            if (line.Contains("<headline>"))
                            {
                                //para sacar titular
                                headLineText = ConsolaEWBS.ExtraerTexto(line);
                            }

                            if ((!string.IsNullOrWhiteSpace(headLineText)) && isMagCreationDate)
                            {
                                
                                arrAux=headLineText.Split(' ');
                                magnitude = arrAux[0];

                                if (!string.IsNullOrWhiteSpace(headLineText))
                                {
                                    main.AlertMessage = headLineText;
                                    ConsolaEWBS.inicio = DateTime.UtcNow;
                                    Console.WriteLine(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio) + ": Headline: " + headLineText);

                                    Console.WriteLine(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio) + ": Magnitude: " + magnitude);
                                    Console.WriteLine(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio) + ": Magnitude Creation Time: " + ConsolaEWBS.FormatFecha(magCreationDate));
                                    Console.WriteLine(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio) + ": Sent Time: " + ConsolaEWBS.FormatFecha(sendDate));
                                    Console.WriteLine(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio) + ": Reception Time: " + ConsolaEWBS.FormatFecha(receptionDate));

                                    Console.WriteLine(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio) + ": Timespan Diff ST-MCT: " + ConsolaEWBS.CalcularTimeSpan(magCreationDate, sendDate));
                                    Console.WriteLine(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio) + ": Timespan Diff RT-ST: " + ConsolaEWBS.CalcularTimeSpan(sendDate, receptionDate));

                                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio), ConsolaEWBS.path(), "Headline: " + headLineText);

                                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio), ConsolaEWBS.path(), "Magnitude: " + magnitude);
                                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio), ConsolaEWBS.path(), "Magnitude Creation Time: "+ConsolaEWBS.FormatFecha(magCreationDate));
                                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio), ConsolaEWBS.path(), "Sent Time: " + ConsolaEWBS.FormatFecha(sendDate));
                                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio), ConsolaEWBS.path(), "Reception Time: " + ConsolaEWBS.FormatFecha(receptionDate));
                                    
                                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio), ConsolaEWBS.path(), "Timespan Diff ST-MCT: " + ConsolaEWBS.CalcularTimeSpan(magCreationDate, sendDate));
                                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(ConsolaEWBS.FormatFecha(ConsolaEWBS.inicio), ConsolaEWBS.path(), "Timespan Diff RT-ST: " + ConsolaEWBS.CalcularTimeSpan(sendDate, receptionDate));

                                    main.ejecutarAcciones(main.getBotonIndex(1));

                                    if (main.TieneTimer)
                                    {
                                        System.Threading.Thread.Sleep(TimeSpan.FromSeconds(main.EwbsTimer));

                                        main.ejecutarAcciones(main.getBotonIndex(3));
                                    }
                                    main.CierreDeAplicacion();
                                }                                
                                break;
                            }
                            position = position + 1;
                        }
                        initial = ConsolaEWBS.ReadLines(ruta);
                    }
                }

            }
            catch (Exception ex)
            {
                Console.WriteLine("Error during process of Messages: " + ex.Message);
                ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), "Error during process of Messages: " + ex.Message);
            }
                

            //ITERACION INDEFINIDA            

            

        }

        private static void Folder(FolderOptions opts)
        {
            ConsolaEWBS main = new ConsolaEWBS();
            main.CargarCosas();            
            main.ejecutarAcciones(main.getBotonIndex(4));             
        }





        private static void HandleParseError(IEnumerable errs)
        {
            foreach (object err in errs)
            {
                if (err.ToString().ToUpper().Contains("VERSION"))
                {
                    break;
                }

                if (err.ToString().ToUpper().Contains("HELP"))
                {
                    break;
                }

                if (err.ToString().ToUpper().Contains("MISSION"))
                {
                    ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), "Error: [" + err.GetType().GetProperty("Tag").GetValue(err, null) + " " + ((CommandLine.NameInfo)err.GetType().GetProperty("NameInfo").GetValue(err, null)).NameText + "]");
                }
                else
                {
                    try
                    {
                        ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") ,ConsolaEWBS.path(), "Error: [" + err.GetType().GetProperty("Tag").GetValue(err, null) + " " + err.GetType().GetProperty("Token").GetValue(err, null) + "]");
                    }
                    catch (Exception) { }
                }
            }
        }

        [Verb("connect", HelpText = "Connect to Server")]
        class ConnectOptions
        {
            [Option('i', "ip", Required = false, HelpText = "IP (optional)")]
            public string IP { get; set; }
        }

        [Verb("send", HelpText = "Send message")]
        class SendOptions
        {
            [Option('i', "ip", Required = false, HelpText = "IP (optional)")]
            public string IP { get; set; }

            [Option('a', "area", Required = false, HelpText = "Area Code (optional)")]
            public string Area { get; set; }

            [Option('t', "timer", Required = false, HelpText = "Timer (optional)")]
            public string Timer { get; set; }

            [Option('e', "emergency", Required = false, HelpText = "Alert Type:\n1)Special\n2)Normal")]
            public string Emergency { get; set; }

            [Option('m', "message", Required = true, HelpText = "Message for transmition")]
            public string Message { get; set; }
        }

        [Verb("stop", HelpText = "Stop message")]
        class StopOptions
        {
            [Option('i', "ip", Required = false, HelpText = "IP (optional)")]
            public string IP { get; set; }
        }

        [Verb("monitor", HelpText = "Monitor stomp events file.")]
        class MonitorOptions
        {
            [Option('i', "ip", Required = false, HelpText = "IP (optional)")]
            public string IP { get; set; }

            [Option('a', "area", Required = false, HelpText = "Area Code (optional)")]
            public string Area { get; set; }

            [Option('t', "timer", Required = true, HelpText = "Timer (Mandatory)")]
            public string Timer { get; set; }

            [Option('e', "emergency", Required = false, HelpText = "Alert Type:\n1)Special\n2)Normal")]
            public string Emergency { get; set; }
             
        }

        [Verb("check", HelpText = "Check message")]
        class CheckOptions
        {
            [Option('i', "ip", Required = false, HelpText = "IP (optional)")]
            public string IP { get; set; }
        }

        [Verb("folder", HelpText = "Open Folder")]
        class FolderOptions
        {
        }
    }
}



