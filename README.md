# Group Buy Cli

Group Buy Cli Application. Build for WeBaaS system.

## address-book

An address book is a collection of contact Person information. In this example, you can create person information and add it to your address book.

A person information includes name, email, and a list of phone numbers:

```json
{
    "id": 2,
    "name": "chenyang",
    "email": "jerrycrab@sjtu.edu.cn",
    "phones": {
        "number": "12345678"
    }
}
```

An address book includes a list of person information:

```json
{
    "id": "123",
    "people":[ {
        "id": 1,
        "name": "shenjiahuan",
        "email": "shenjiahuan@sjtu.edu.cn",
        },{
        "id": 2,
        "name": "chenyang",
        "email": "jerrycrab@sjtu.edu.cn",
        "phones":{
            "number": "12345678"},
        }]
}
```

## Build and Run

### Environment

WeBaaS uses Protocol Buffer to store schema definitions. If you haven't installed the compiler, [download the package](https://developers.google.com/protocol-buffers/docs/downloads) and follow the instructions in the README.md file. After installing the protobuf compiler, check the version of it:

```bash
$ protoc --version
```

The minimum version required by WeBaaS is 3.19.0.

Install python dependencies by 

```bash
$ python3 -m pip install -r requirements.txt
```

### Running

Compile schema definitions:

```bash
$ protoc -I=./proto/ --python_out=./ ./proto/*.proto
```

Run the program:

```bash
$ python3 main.py  
```

### Project layout

```json
|- proto/
|    |- address_book.proto                      // defination of address_book and person
|    |- record_metadata_options.proto           // dependency proto 
|    |- record_metadata.proto                   // dependency proto 
|- address_book_pb2.py                          // auto_compiled file of address_book.proto
|- record_metadata_options_pb2.py               // auto_compiled file of record_metadata_options.proto
|- record_metadata_pb2.py                       // auto_compiled file of record_metadata.proto
|- main.py                                      // all logic and main() is here
```
