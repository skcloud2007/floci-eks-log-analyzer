from app.main import parse_line

def test_parse_valid_apache_log_line():
    line = '83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023'
    result = parse_line(line)

    assert result["ip"] == "83.149.9.216"
    assert result["method"] == "GET"
    assert result["url"] == "/presentations/logstash-monitorama-2013/images/kibana-search.png"
    assert result["status"] == "200"

def test_parse_invalid_line():
    line = "this is not apache log"
    result = parse_line(line)

    assert result is None
