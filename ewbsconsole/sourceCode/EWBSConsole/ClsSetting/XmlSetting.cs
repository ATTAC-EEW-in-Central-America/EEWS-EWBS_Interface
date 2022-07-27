using EWBSConsole.ClzMain;
using System;

namespace Apl
{
    namespace Settings
    {
        /// <summary>
        /// XmlSettings class
        /// </summary>
        public class XmlSettings
        {
            #region XmlSettings class
            private string[] _value = new string[10];

            /// <summary>
            /// XmlSettings property
            /// </summary>
            public string[] Value
            {
                get { return _value; }
                set { _value = value; }
            }

            /// <summary>
            /// Read xml settings file
            /// </summary>
            /// <param name="pathFileName">Xml settings path file name</param>
            /// <param name="settings">Xml settings object</param>
            public void ReadXmlSettingFile(string pathFileName, ref XmlSettings settings)
            {
                try
                {
                    // If the xml settings file exists
                    if (System.IO.File.Exists(pathFileName))
                    {
                        System.Xml.Serialization.XmlSerializer serializer = new System.Xml.Serialization.XmlSerializer(typeof(XmlSettings));
                        System.IO.StreamReader sr = new System.IO.StreamReader(pathFileName, new System.Text.UTF8Encoding(false));
                        settings = (XmlSettings)serializer.Deserialize(sr);
                        sr.Close();
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                }
                finally
                {
                }
            }

            /// <summary>
            /// Write xml settings file
            /// </summary>
            /// <param name="pathFileName">Xml settings path file name</param>
            /// <param name="settings">Xml settings object</param>
            public void WriteSettingFile(string pathFileName, XmlSettings settings)
            {
                try
                {
                    System.Xml.Serialization.XmlSerializer serializer = new System.Xml.Serialization.XmlSerializer(typeof(XmlSettings));
                    System.IO.StreamWriter sw = new System.IO.StreamWriter(pathFileName, false, new System.Text.UTF8Encoding(false));
                    serializer.Serialize(sw, settings);
                    sw.Close();
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    EWBSConsole.ClsLog.LogCustom.AlternativeLog(System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"), ConsolaEWBS.path(), ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                }
                finally
                {
                }
            }
            #endregion
        }
    }
}
