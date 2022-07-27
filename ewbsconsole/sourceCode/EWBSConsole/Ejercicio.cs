using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
namespace EWBSConsole
{
    public class Ejercicio
    {
        public static TcpClient sock;

        public static void Main(string[] args)
        {

            TcpListener serverSocket = new TcpListener(8888);
            int requestCount = 0;
            TcpClient clientSocket = default(TcpClient);
            serverSocket.Start();
            Console.WriteLine(" >> Server Started");
            clientSocket = serverSocket.AcceptTcpClient();
            Console.WriteLine(" >> Accept connection from client");
            requestCount = 0;

            while ((true))
            {
                try
                {
                    requestCount = requestCount + 1;
                    NetworkStream networkStream = clientSocket.GetStream();
                    byte[] bytesFrom = new byte[10025];
                    //networkStream.Read(bytesFrom, 0, (int)clientSocket.ReceiveBufferSize);

                    networkStream.Read(bytesFrom, 0, bytesFrom.Length);
                    
                    string dataFromClient = System.Text.Encoding.ASCII.GetString(bytesFrom);
                    
                    if (!string.IsNullOrWhiteSpace(dataFromClient.Trim()))
                    {
                        Console.WriteLine(" >> Data from client - " + dataFromClient.Trim());
                        System.Threading.Thread.Sleep(2000);
                    }
                    //string serverResponse = "Last Message from client" + dataFromClient;
                    //Byte[] sendBytes = Encoding.ASCII.GetBytes(serverResponse);
                    //networkStream.Write(sendBytes, 0, sendBytes.Length);
                    //networkStream.Flush();
                    //Console.WriteLine(" >> " + serverResponse);

                    //System.Threading.Thread.Sleep(100000);
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                    System.Threading.Thread.Sleep(100000);
                }
            }

            clientSocket.Close();
            serverSocket.Stop();
            Console.WriteLine(" >> exit");
            Console.ReadLine();
        }
    }
}
