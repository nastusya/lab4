FROM golang

RUN go get github.com/justsocialapps/kafkabeat
WORKDIR $GOPATH/src/github.com/justsocialapps/kafkabeat
RUN make

COPY kafkabeat.yml .

CMD ./kafkabeat -c kafkabeat.yml -e -d "*"